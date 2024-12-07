from rest_framework import serializers
from .models import Imagen, Busqueda  


class ImagenSerializer(serializers.ModelSerializer):  
    class Meta:  
        model = Imagen  
        fields = '__all__'  


class BusquedaSerializer(serializers.ModelSerializer):  
    imagen = ImagenSerializer()  # Anida el serializador de Imagen dentro del serializador de Busqueda.

    class Meta:  
        model = Busqueda  
        fields = '__all__'  
        
    # Método personalizado para manejar la creación de una instancia de Busqueda con datos anidados.
    def create(self, validated_data):  
        imagen_data = validated_data.pop('imagen')  # Extrae los datos de 'imagen' de los datos validados.
        imagen = Imagen.objects.create(**imagen_data)  # Crea una nueva instancia de Imagen con los datos extraídos.
        busqueda = Busqueda.objects.create(imagen=imagen, **validated_data)  # Crea una nueva instancia de Busqueda asociada a la imagen recién creada.
        return busqueda  # Devuelve la instancia de Busqueda creada.

    # Método personalizado para manejar la actualización de una instancia de Busqueda con datos anidados.
    def update(self, instance, validated_data):  
        imagen_data = validated_data.pop('imagen')  # Extrae los datos de 'imagen' de los datos validados.
        imagen = instance.imagen  # Obtiene la instancia de Imagen asociada al registro de Busqueda.
        for attr, value in imagen_data.items():  # Itera sobre los datos de la imagen.
            setattr(imagen, attr, value)  # Actualiza los atributos de la imagen con los nuevos valores.
        imagen.save()  # Guarda los cambios en la instancia de Imagen.
        for attr, value in validated_data.items():  # Itera sobre los datos restantes de Busqueda.
            setattr(instance, attr, value)  # Actualiza los atributos de la instancia de Busqueda con los nuevos valores.
        instance.save()  # Guarda los cambios en la instancia de Busqueda.
        return instance  # Devuelve la instancia de Busqueda actualizada.
