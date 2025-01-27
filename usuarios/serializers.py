from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from .models import Usuarios, Ubicacion


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = Usuarios
        """Campos que se incluyen en el serializador"""
        fields = ["id", "email", "name", 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def validate_email(self, value):
        # Covierte el email a LowerCase
        norm_email = value.lower()
        # Revisa si el email ya existe email__ixact es un filtro que busca sin tener en cuenta mayusculas y/o minusculas y que no este eliminado
        if Usuarios.objects.filter(email__iexact=norm_email, is_deleted=False).exists():
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
        model = Usuarios
        fields = ['name', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True}}

class UbicacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ubicacion
        fields = ["id", "nombre", "latitud", "longitud"]

class PasswordChangeSerializer(serializers.Serializer):
    new_password = serializers.CharField(write_only=True, min_length=8, max_length=128)
    confirm_password = serializers.CharField(write_only=True, min_length=8, max_length=128)

    def validate(self, data):
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError("Las contraseñas no coinciden.")
        return data