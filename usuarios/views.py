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


# Create your views here.
# Vista de Registro Usuarios
class RegisterView(generics.CreateAPIView):
    queryset = Usuarios.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

# Vista Para Logearse  
class CustomTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        try:
            response = super().post(request, *args, **kwargs)
        except AuthenticationFailed:
            raise AuthenticationFailed("Las credenciales proporcionadas no son correctas.")
        return response

# Vista Para Perfil de usuario autenticado
class ProfileView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ProfileOutputSerializer
    
    # Metodo que define el usuario que se debe devolver
    def get_object(self):
        return self.request.user
    
    
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
