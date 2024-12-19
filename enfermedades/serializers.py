from rest_framework import serializers
from .models import Tratamiento, Enfermedad

class TratamientoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tratamiento
        fields = ["descripcion", "fuente"]

class EnfermedadSerializer(serializers.ModelSerializer):
    tratamientos = TratamientoSerializer(many = True, read_only=True)
    class Meta:
        model = Enfermedad
        fields = ["id", "nombre", "tratamiento"]