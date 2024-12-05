from .models import Usuarios
from .serializers import UserSerializer, ProfileOutputSerializer, UserUpdateSerializer
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

    # TODO REVISAR SOFT-DELETE USER
    def delete(self, request, *args, **kwargs):
        user = request.user  # Obtiene el usuario autenticado.
        print(user)
        user.delete()  # Elimina el usuario de la base de datos.
        return Response({"message": "Usuario eliminado exitosamente."}, status=status.HTTP_204_NO_CONTENT)  # Mensaje de éxito.

# TODO CUIDADO ESTO SE TIENE QUE REVISAR SI SE VA PERMITIR RESTAURAR UN USUARIO ELIMINADO
class UserRestoreView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, email):
        try:
            user = Usuarios.objects.all_with_deleted().filter(email=email, is_deleted=True).first()
            print(user)
            user.restore()
            return Response({"mensaje": f"usuario {user.email} restaurado"}, status=status.HTTP_200_OK)
        except Usuarios.DoesNotExist:
            return Response({"detail": "Usuario no encontrado o no soft-deleted."}, status=status.HTTP_404_NOT_FOUND)