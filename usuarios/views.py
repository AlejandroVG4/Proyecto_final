from .models import Usuarios
from .serializers import UserSerializer
from rest_framework.permissions import AllowAny
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
