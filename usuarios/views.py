from .models import Usuarios
from .serializers import UserSerializer, ProfileOutputSerializer, UserUpdateSerializer
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


# Vista para el registro de usuarios
class RegisterView(generics.CreateAPIView):
    queryset = Usuarios.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

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
    permission_classes = [IsAuthenticated]  # Solo accesible para usuarios autenticados.
    queryset = Usuarios.objects.all()  # Recupera todos los usuarios.
    serializer_class = UserUpdateSerializer  # Usa el serializador UserUpdateSerializer para PUT y PATCH.

    def update(self, request, *args, **kwargs):
        partial = kwargs.get('partial', False)  # Detecta si es un PATCH (parcial).
        instance = request.user # Obtiene el usuario a actualizar.
        # Encripta la contraseña
        if "password" in request.data:
            request.data["password"] = make_password(request.data["password"])

        invalid_fields = [field for field in request.data.keys() if field not in ['name', 'email', 'password']]
        if invalid_fields:
            if len(invalid_fields) == 1:
                error_message = f"El campo {invalid_fields[0]} no es válido."
            else:
                error_message = f"Los campos {', '.join(invalid_fields)} no son válidos."

            return Response({"error": error_message}, status=status.HTTP_400_BAD_REQUEST)
        serializer = self.get_serializer(instance, data=request.data, partial=partial)  # Valida y serializa los datos.
        serializer.is_valid(raise_exception=True)  # Valida los datos del serializador.
        self.perform_update(serializer)  # Guarda los cambios en la base de datos.
        return Response(serializer.data)  # Retorna los datos actualizados.

    def perform_update(self, serializer):
        serializer.save()  # Guarda el usuario actualizado.

    # Llama el metodo delete del modelo
    def delete(self, request, *args, **kwargs):
        user = request.user  # Obtiene el usuario autenticado.
        print(user)
        user.delete()  # Elimina el usuario de la base de datos.
        return Response({"message": "Usuario eliminado exitosamente."}, status=status.HTTP_204_NO_CONTENT)  # Mensaje de éxito.

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

        # Generar el token y uid que se envian en la url
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(str(user.pk).encode())

        # Url de restablecimiento de contraseña (Debe ser cambiada por un deep link)
        reset_url = request.build_absolute_uri(reverse('password_reset_confirm', kwargs={'uidb64' : uid, 'token' : token}))

        # Asunto y mensaje del correo
        subject = "Solicitud de restablecimiento de contraseña"
        message = render_to_string(self.email_template_name, {
            'reset_url' : reset_url,
            'user' : user
        })

        # Funcion que envia el email al usuario
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email], html_message=message)
        return Response({'message' : 'Correo de restablecimiento enviado exitosamente'}, status=status.HTTP_200_OK)