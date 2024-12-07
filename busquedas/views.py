from django.http import JsonResponse
from .utils.getSasUrl import get_sas_url
from .utils.visionAnalysis import analyze_image
from .utils.getTreatment import get_treatment
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated

from .models import Busqueda, Imagen
from enfermedades.models import Enfermedad
from usuarios.models import Ubicacion
from .serializers import BusquedaSerializer
from rest_framework import generics


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
        print("En peticion post")

        # Obtener la url de la imagen de la request
        img_url = request.data.get('img_url')
        print("url de la imagen", img_url)

        # Obtener el Usuario logeado de la request
        user = request.user
        print("usuario de la busqueda", user)

        if not img_url:
            return Response({"error": "Imagen Requerida"}, status=status.HTTP_400_BAD_REQUEST)

        illness = analyze_image(img_url)
        treatment_dict = get_treatment(illness)

        # Guardamos la url de la imagen en la base de datos
        # TODO se va a dejar subir una imagen varias veces?
        img = Imagen.objects.create(url=img_url)


        # Obtener la pk de la enfermedad 
        illness_instancia = Enfermedad.objects.get(id=treatment_dict["illness_pk"])
        print(illness_instancia)

        # Obtener el tratamiento y fuente para devolver al front
        treatment = treatment_dict["tratamiento"]
        print(treatment)

        ubicacion_prueba = Ubicacion.objects.get(id=1)

        print("Guradando Busqueda")
        # Crear la busqueda 
        busqueda = Busqueda.objects.create(
            enfermedad = illness_instancia,
            ubicacion = ubicacion_prueba,
            imagen = img,
            usuario = user
        )


        # Aqui construimos el diccionario para entregar los resultados al front
        result = {
            "illness" : illness,
            "url" : img_url,
            "treatment" : treatment
        }

        if "error" in result:
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(result, status=status.HTTP_200_OK)


class BusquedaListCreateView(generics.ListCreateAPIView):
    queryset = Busqueda.objects.all()
    serializer_class = BusquedaSerializer

class BusquedaDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Busqueda.objects.all()
    serializer_class = BusquedaSerializer
