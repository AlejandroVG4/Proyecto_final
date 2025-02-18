from .models import Usuarios
from .serializers import UserSerializer, ProfileOutputSerializer, UserUpdateSerializer, PasswordChangeSerializer
from django.contrib.auth.hashers import make_password
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.exceptions import AuthenticationFailed
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from django.contrib.auth.views import PasswordResetView
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.shortcuts import render
from django.http import JsonResponse
from django.conf import settings
from django.urls import reverse
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.http import HttpResponsePermanentRedirect

from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.http import JsonResponse
import urllib.parse

from rest_framework_simplejwt.token_blacklist.models import OutstandingToken
from django.contrib.auth.models import update_last_login
from busquedas.models import Busqueda
from busquedas.serializers import BusquedaAnalisiSerializer

class CustomRedirect(HttpResponsePermanentRedirect):
    allowed_schemes = ['eva','http', 'https']

# Vista para el registro de usuarios
class RegisterView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    queryset = Usuarios.objects.all()
    serializer_class = UserSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            try:
                self.perform_create(serializer)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            except IntegrityError as e:
                if 'usuarios_email_key' in str(e):
                    return Response({'email' : ["El correo electrónico ya está registrado."]}, status=status.HTTP_400_BAD_REQUEST)
                raise e
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
# Vista para la obtención de un token de acceso al iniciar sesión
class CustomTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        try:
            response = super().post(request, *args, **kwargs)
        except AuthenticationFailed:
            raise AuthenticationFailed("Las credenciales proporcionadas no son correctas.")
        return response

# Vista para obtener el perfil del usuario autenticado
class ProfileView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ProfileOutputSerializer
    # Metodo que define el usuario que se debe devolver
    def get_object(self):
        return self.request.user

# Vista para actualizar o eliminar un usuario autenticado
class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Usuarios.objects.all()
    serializer_class = UserUpdateSerializer

    def update(self, request, *args, **kwargs):
        partial = kwargs.get('partial', False)
        instance = request.user  

        # Solo permitimos modificar 'name' y 'password'
        invalid_fields = [field for field in request.data.keys() if field not in self.serializer_class.Meta.fields]
        if invalid_fields:
            return Response({"error": f"Los campos {', '.join(invalid_fields)} no son válidos."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if "password" in request.data:
            tokens = OutstandingToken.objects.filter(user=instance)
            for token in tokens:
                token.delete()  

            return Response({"message": "Contraseña actualizada. Debes iniciar sesión nuevamente."}, status=status.HTTP_200_OK)

        return Response(serializer.data)

    def perform_update(self, serializer):
        instance = serializer.save()
        update_last_login(None, instance)  # Actualiza la última sesión del usuario

    def delete(self, request, *args, **kwargs):
        user = request.user
        user.delete()
        return Response({"message": "Usuario eliminado exitosamente."}, status=status.HTTP_204_NO_CONTENT)

# Vista para enviar enlace de restauración de contraseña al correo del usuario
class CustomPasswordResetView(APIView):

    # Plantilla del mensaje del email
    email_template_name = 'password_reset_email.html'

    def post(self, request, *args, **kwargs):

        # Extraer el email de la request
        email = request.data.get('email')

        # Verificar si email no es enviado en la solicitud
        if not email:
            return Response({'error' : 'Ingresa un correo electrónico'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Verificar que sea un email valido
            validate_email(email)
            # Extraer el usuario con el email indicado
            # Verificar que el email no pertenezca a un usuario desactivado o eliminado
            user = Usuarios.objects.get(email=email, is_deleted=False)
        except ValidationError as e:
            print("Email incorrecto, detalle", e)
            mensaje_error = e.messages[0]
            return Response({'error' : mensaje_error}, status=status.HTTP_400_BAD_REQUEST)
        except Usuarios.DoesNotExist:
            return Response({'error' : 'El correo electrónico no se encuentra registrado'}, status=status.HTTP_400_BAD_REQUEST)

        # Generar el token y encripto el uid que se envian en la url
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(str(user.pk).encode())

        # Url que llama a vista redirectToDeepLink
        # Url lleva Token y uid
        reset_url  = request.build_absolute_uri(reverse('redirect_to_deep_link', kwargs={'uidb64': uid, 'token' : token}))

        # Asunto y mensaje del correo
        subject = "Solicitud de restablecimiento de contraseña"
        message = render_to_string(self.email_template_name, {
            'reset_url' : reset_url,
            'user' : user
        })

        # Funcion que envia el email al usuario
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email], html_message=message)
        return Response({'message' : 'Correo de restablecimiento enviado exitosamente'}, status=status.HTTP_200_OK)

# Vista para verificar validez del token y UID para restablecer la contraseña.
class CustomPasswordResetConfirmView(APIView):

    def get(self, request, uidb64, token, *args, **kwargs):
        try:
            # Decodificar el UID
            uid = urlsafe_base64_decode(uidb64).decode()
            user = Usuarios.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, Usuarios.DoesNotExist):
            return Response({'error': 'Enlace inválido o usuario no encontrado'}, status=status.HTTP_400_BAD_REQUEST)

        # Verificar el token
        if not default_token_generator.check_token(user, token):
            return Response({'error': 'Token inválido o expirado'}, status=status.HTTP_400_BAD_REQUEST)

        # Generar el deep link para la app móvil
        # deep_link = f"myapp://password-reset/{uidb64}/{token}"
        reset_url = request.build_absolute_uri(
            reverse('password_reset_confirm', kwargs={'uidb64': uidb64, 'token': token})
        )
        # Retornar el deep link para redirigir al formulario de cambio de contraseña
        return Response({'message': 'Token válido', 'reset_url': reset_url}, status=status.HTTP_200_OK)

# Vista para guardar nueva contraseña
class SetNewPasswordView(APIView):

    def post(self, request, uidb64, token, *args, **kwargs):
        serializer = PasswordChangeSerializer(data=request.data)
        if serializer.is_valid():
            new_password = serializer.validated_data['new_password']

            # TODO: Validar si es necesario revisar nuevamente validez de token
            try:
                uid = urlsafe_base64_decode(uidb64).decode()
                user = Usuarios.objects.get(pk=uid)
            except (TypeError, ValueError, OverflowError, Usuarios.DoesNotExist):
                return Response({'error': 'Enlace inválido o usuario no encontrado'}, status=status.HTTP_400_BAD_REQUEST)

            if not default_token_generator.check_token(user, token):
                return Response({'error': 'Token inválido o expirado'}, status=status.HTTP_400_BAD_REQUEST)

            user.set_password(new_password)
            user.save()

            return Response({'message': 'Contraseña actualizada con éxito'}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Vista para redirigir a deepLink
def RedirectToDeepLink(request, uidb64, token):
    deep_link = f"eva://contrasena/{uidb64}/{token}"
    fallback_url = request.build_absolute_uri(reverse("password_reset_fallback", args=[uidb64, token]))

    print("Fallback URL:", fallback_url)

    response_html = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Abrir en Eva</title>
        <script type="text/javascript">
            function openApp() {{
                window.location.href = "{deep_link}";  // Intentar abrir la app
                setTimeout(function() {{
                    window.location.href = "{fallback_url}";  // Si falla, ir a la página de fallback
                }}, 3000);
            }}
            document.addEventListener("DOMContentLoaded", openApp);
        </script>
    </head>
    <body>
        <p>Cargando...</p>
    </body>
    </html>
    """
    print("Fallback URL:", fallback_url)
    return HttpResponse(response_html)

# Ofrece una opcion de restablecer contraseña en la web
def PasswordResetFallbackView(request, uidb64, token):
    deep_link = f"eva://contrasena/{uidb64}/{token}"
    return render(request, "fallback.html", {"deep_link": deep_link})

# Vista que genera datos de analisis estadistico
class Estadisticas(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Busqueda.objects.all()
    serializer_class = BusquedaAnalisiSerializer

    def get_queryset(self):
        user = self.request.user
        return Busqueda.objects.filter(usuario=user)
    
