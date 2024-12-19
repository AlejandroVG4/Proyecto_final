from rest_framework.serializers import ModelSerializer, PrimaryKeyRelatedField
from .models import Imagen, Busqueda
from enfermedades.models import Enfermedad
from enfermedades.serializers import EnfermedadSerializer
from usuarios.models import Usuarios, Ubicacion
from usuarios.serializers import UbicacionSerializer


class ImagenSerializer(ModelSerializer):
    class Meta:
        model = Imagen
        fields = '__all__'


class BusquedaSerializer(ModelSerializer):
    # Aceptar las llaves primarias de los campos
    enfermedad_id = PrimaryKeyRelatedField(queryset = Enfermedad.objects.all(), source = 'enfermedad', write_only = True)
    ubicacion_id = PrimaryKeyRelatedField(queryset = Ubicacion.objects.all(), source = 'ubicacion', write_only = True )
    imagen_id = PrimaryKeyRelatedField(queryset = Imagen.objects.all(), source = 'imagen', write_only = True )
    usuario_id = PrimaryKeyRelatedField(queryset = Usuarios.objects.all(), source = 'usuario', write_only = True )

    # Devuelva los detalles de cada campo y no solo el id
    enfermedad = EnfermedadSerializer(read_only=True)
    ubicacion = UbicacionSerializer(read_only = True)
    imagen = ImagenSerializer(read_only = True)

    class Meta:
        model = Busqueda
        fields = [
            'id',
            'enfermedad',
            'ubicacion',
            'imagen',
            'usuario',
            'enfermedad_id',
            'ubicacion_id',
            'imagen_id'
        ]


