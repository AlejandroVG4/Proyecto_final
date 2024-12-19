from .utils.getSasUrl import get_sas_url
from .utils.visionAnalysis import analyze_image
from .utils.getTreatment import get_treatment
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from .models import Busqueda, Imagen
from enfermedades.models import Enfermedad
from usuarios.models import Ubicacion, Usuarios
from .serializers import BusquedaSerializer
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView


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
                {"error": "Imagen Requerida"},
                status=status.HTTP_400_BAD_REQUEST
                )

        # Guardamos la url de la imagen en la base de datos
        img = Imagen.objects.create(url=img_url)

        # Llama la funcion para obtener el nombre de la enfermedad
        illness = analyze_image(img_url)

        # Instancias de los campos del modelo búsquedas
        enfermedad = Enfermedad.objects.get(nombre=illness)
        usuario = Usuarios.objects.get(id=request.user.id)
        
        # Revisar si viene ubicacion el la request
        ubicacion_data = request.data.get('ubicacion')
        
        if not ubicacion_data:
            ubicacion = Ubicacion.objects.filter(nombre="Ubicación no disponible").first()
             

        if not(enfermedad and usuario and ubicacion):
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
                    "búsqueda" : busqueda
                },
                status = status.HTTP_200_OK
            )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Vista que devuelve la lista de busquedas por usuario
class BusquedaListView(ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Busqueda.objects.all()
    serializer_class = BusquedaSerializer

    def get_queryset(self):
        user = self.request.user
        return Busqueda.objects.filter(usuario=user)

class BusquedaDetailView(RetrieveUpdateDestroyAPIView):
    queryset = Busqueda.objects.all()
    serializer_class = BusquedaSerializer


