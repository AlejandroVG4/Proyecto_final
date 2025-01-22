from .utils.getSasUrl import get_sas_url
from .utils.visionAnalysis import analyze_image, check_if_plant
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from .models import Busqueda, Imagen
from enfermedades.models import Enfermedad
from usuarios.models import Ubicacion, Usuarios
from .serializers import BusquedaSerializer
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.pagination import LimitOffsetPagination
from django.utils.translation import gettext as _


# Create your views here.

class GenerateSasUrlView(APIView):

    # TODO Restringir
    permission_classes = [AllowAny]

    def get(self, request):

        try:
            url = get_sas_url()
            return Response({"url" : url}, status=status.HTTP_200_OK)
        except Exception as e:
            print(e)

# Imagen de prueba

class AnalyzeImageView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Extraer la url de la imagen de la request
        img_url = request.data.get('img_url')

        if not img_url:
            return Response(
                {"error": _("Image required")},
                status=status.HTTP_400_BAD_REQUEST
                )

        # Llama la funcion para verificar si es planta
        is_plant, mensaje = check_if_plant(img_url)
        print(is_plant, mensaje)
        if is_plant != True:
            print(is_plant)
            return Response(
                {"error": mensaje},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Guardamos la url de la imagen en la base de datos
        img = Imagen.objects.create(url=img_url)

        # Llama la funcion para obtener el nombre de la enfermedad
        illness = analyze_image(img_url)

        print("Pase illness Vista", illness)
        # Instancias de los campos del modelo búsquedas
        enfermedad = Enfermedad.objects.get(nombre=illness)
        usuario = Usuarios.objects.get(id=request.user.id)

        # Revisar si viene ubicacion el la request
        ubicacion_data = request.data.get('ubicacion')

        # Si no tiene ubicacion asigna una por defecto
        if not ubicacion_data:
            ubicacion = Ubicacion.objects.filter(nombre="Ubicación no disponible").first()

        # Si falta algun dato de la busqueda
        if not(enfermedad and usuario and ubicacion):
            print(illness, usuario, ubicacion)
            return Response(
                {"error" : "Datos de búsqueda incompletos"},
                status=status.HTTP_400_BAD_REQUEST
            )

        busqueda_data = {
            "enfermedad_id" : enfermedad.id,
            "usuario_id" : usuario.id,
            "imagen_id" : img.id,
            "ubicacion_id" : ubicacion.id,
            "enfermedad" : enfermedad,
            "ubicacion" : ubicacion,
            "imagen" : img
        }

        serializer = BusquedaSerializer(data=busqueda_data)
        if serializer.is_valid():
            serializer.save()
            busqueda = serializer.data
            return Response(
                {
                    "mensaje" : "Búsqueda creada con éxito",
                    "busqueda" : busqueda
                },
                status = status.HTTP_200_OK
            )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Paginacion
class BusquedaPagination(LimitOffsetPagination):
    default_limit = 5 # Limite predeterminado
    max_limit = 20 # Limite maximo permitido

# Vista que devuelve la lista de busquedas por usuario
# URL peticion con paginacion: ?limit=3

class BusquedaListView(ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Busqueda.objects.all()
    serializer_class = BusquedaSerializer
    # Clase que define como manejar la pagination
    pagination_class = BusquedaPagination

    def get_queryset(self):
        user = self.request.user
        return Busqueda.objects.filter(usuario=user)

class BusquedaDetailView(RetrieveUpdateDestroyAPIView):
    queryset = Busqueda.objects.all()
    serializer_class = BusquedaSerializer


