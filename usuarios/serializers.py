from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from .models import Usuarios


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = Usuarios
        """Campos que se incluyen en el serializador"""
        fields = ["id", "email", "name", 'password']
        extra_kwargs = {'password': {'write_only': True}}

    
    def validate_email(self, value):
        # Covierte el email a LowerCase
        norm_email = value.lower()
        print(norm_email, value)

        # Revisa si el email ya existe email__ixact es un filtro que busca sin tener en cuenta mayusculas y/o minusculas
        if Usuarios.objects.filter(email__iexact=norm_email).exists():
            raise ValidationError("Este correo electrónico ya está registrado.")
        
        return norm_email

    def create(self, validated_data):
        usuario = Usuarios.objects.create_user(**validated_data)
        return usuario

class ProfileOutputSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuarios
        fields = ['name', 'email']
        
class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model: Usuarios
        fields = ['name', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True}}