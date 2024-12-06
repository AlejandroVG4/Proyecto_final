from rest_framework import serializers
from .models import Tratamiento

class TratamientoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tratamiento
        fields = ["descripcion", "fuente"]