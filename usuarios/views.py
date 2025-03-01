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
import pandas as pd

from rest_framework_simplejwt.token_blacklist.models import OutstandingToken
from django.contrib.auth.models import update_last_login
from busquedas.models import Busqueda
from enfermedades.models import Enfermedad
from usuarios.models import Ubicacion, Usuarios
from .utils.utils import encontrar_moda, encontrar_moda_ubicacion, contar_plantas_por_salud
from django.utils.translation import gettext as _

from rest_framework_simplejwt.tokens import RefreshToken

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
class StatisticsAnalysisView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):

        # Verificar que el usuario tenga busquedas
        usuario = request.user
        if not usuario.busquedas.exists():
            return Response({
                "error" : "El usuario no tiene búsquedas registradas"
            }, status=status.HTTP_404_NOT_FOUND)

        # Obtener las busquedas del usuario autenticado
        busquedas = Busqueda.objects.filter(usuario=request.user)

        # Convertir los datos en una lista de diccionarios
        data = list(busquedas.values("fecha_creacion","enfermedad","ubicacion","usuario"))

        # Convertir en un DataFrame
        data_frame = pd.DataFrame(data)
        #print(data_frame)

        # LLamar funciones de analisis
        # Variable que almacena resultados de la funcion que encuentra la moda en un periodo de 30 dias
        datos_moda_30d = encontrar_moda(data_frame)

        # Buscar nombre enfermedad en la BD y asignarla a la clave enfermedad del diccionario
        datos_moda_30d["enfermedad"] = _((Enfermedad.objects.filter(id=datos_moda_30d["enfermedad"]).first()).nombre)

        #Si no encuentra la enfermedad
        if len(datos_moda_30d["enfermedad"]) <= 0:
            return Response({
                "error" : "Enfermedad No encontrada"
            }, status=status.HTTP_404_NOT_FOUND)

        # Moda ubicaciones
        datos_moda_ubicaciones = encontrar_moda_ubicacion(data_frame)

        for item in datos_moda_ubicaciones:
            # Buscar nombre ubicacion en la BD y asignarla a la clave ubicacion del diccionario
            item['ubicacion'] = (Ubicacion.objects.filter(id=item['ubicacion']).first()).nombre

            #Si no encuentra la enfermedad
            if len(item['ubicacion']) <= 0:
                return Response({
                    "error" : "Ubicacion No encontrada"
                }, status=status.HTTP_404_NOT_FOUND)

            # Buscar nombre enfermedad en la BD y asignarla a la clave enfermedad del diccionario
            item['enfermedad'] = _((Enfermedad.objects.filter(id=item['enfermedad']).first()).nombre)

            #Si no encuentra la enfermedad
            if len(item['enfermedad']) <= 0:
                return Response({
                    "error" : "Enfermedad No encontrada"
                }, status=status.HTTP_404_NOT_FOUND)   

        datos_conteo_enfermedades = contar_plantas_por_salud(data_frame)
        conteo_registros_dict = {}

        for clave in datos_conteo_enfermedades.keys():
            clave_nombre =_((Enfermedad.objects.filter(id=clave).first()).nombre)

            #Si no encuentra la enfermedad
            conteo_registros_dict[clave_nombre] = datos_conteo_enfermedades[clave]
            if len(item['enfermedad']) <= 0:
                return Response({
                    "error" : "Enfermedad No encontrada"
                }, status=status.HTTP_404_NOT_FOUND) 

        return Response({
            "estadisticas" : {
                "frecuencia_por_fecha" : datos_moda_30d,
                "frecuencia_por_ubicacion" : datos_moda_ubicaciones,
                "conteo_enfermedades" : conteo_registros_dict
            }
        })

# El frontend debe enviar el refresh_token en el body de la petición para invalidarlo.
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            token = RefreshToken(refresh_token)
            token.blacklist()  # Invalida el token de refresh
            return Response({"message": "Logout exitoso"}, status=200)
        except Exception as e:
            return Response({"error": "Token inválido"}, status=400)