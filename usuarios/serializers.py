from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from .models import Usuarios, Ubicacion
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.hashers import make_password


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
        fields = ['name']
        read_only_fields = ['email']
        extra_kwargs = {'password': {'write_only': False}}

    def validate(self, data):

        forbidden_fields = ['email', 'password']
        
        fields_in_data = [field for field in forbidden_fields if field in self.initial_data]
        # Si intentan actualizar el email o password

        if fields_in_data:
            raise serializers.ValidationError({
                "Error": f"No puedes modificar los siguientes campos: {', '.join(fields_in_data)}"
            })
        return data

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

# Serializador para el cambio de contraseña de usuario autenticado
class PasswordUpdateSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)

    def validate_new_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError(" La nueva contraseña debe tener al menos 8 caracteres")
        return value

    def validate(self, data):
        user = self.context['request'].user

        if not user.check_password(data['old_password']):
            raise serializers.ValidationError({"old_password": "La contraseña actual no es correcta."})
        return data

    def save(self):
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return {"message": "Contraseña actualizada con éxito."}