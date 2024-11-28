from .models import Usuarios
from .serializers import UserSerializer, ProfileOutputSerializer, UserUpdateSerializer
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.exceptions import AuthenticationFailed
from rest_framework import generics


# Create your views here.
class RegisterView(generics.CreateAPIView):
    queryset = Usuarios.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

# Para Logearse  
# TO DO CUSTOM TOKEN  
class CustomTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        try:
            response = super().post(request, *args, **kwargs)
        except AuthenticationFailed:
            raise AuthenticationFailed("Las credenciales proporcionadas no son correctas.")
        return response
    
class ProfileView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ProfileOutputSerializer
    
    def get_object(self):
        return self.request.user
    
    
class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Usuarios.objects.all()  # Recupera todos los usuarios.
    permission_classes = [IsAuthenticated]  # Solo accesible para usuarios autenticados.
    serializer_class = UserUpdateSerializer  # Usa el serializador UserUpdateSerializer para PUT y PATCH.

    def update(self, request, *args, **kwargs):
        partial = kwargs.get('partial', False)  # Detecta si es un PATCH (parcial).
        instance = self.get_object()  # Obtiene el usuario a actualizar.
        serializer = self.get_serializer(instance, data=request.data, partial=partial)  # Valida y serializa los datos.
        serializer.is_valid(raise_exception=True)  # Valida los datos del serializador.
        self.perform_update(serializer)  # Guarda los cambios en la base de datos.
        return Response(serializer.data)  # Retorna los datos actualizados.

    def perform_update(self, serializer):
        serializer.save()  # Guarda el usuario actualizado.

    def delete(self, request, *args, **kwargs):
        user = self.get_object()  # Obtiene el usuario a eliminar.
        user.delete()  # Elimina el usuario de la base de datos.
        return Response({"message": "Usuario eliminado exitosamente."}, status=status.HTTP_204_NO_CONTENT)  # Mensaje de éxito.
