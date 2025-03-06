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
from usuarios.serializers import UbicacionSerializer
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.pagination import LimitOffsetPagination
from django.utils.translation import gettext as _
from .utils.geocoding import get_location_name
from .utils.getUbicationIp import obtener_ubicacion
from decimal import Decimal
import pandas as pd
from .utils.utils import encontrar_moda, encontrar_moda_ubicacion, contar_plantas_por_salud


# Create your views here.

class GenerateSasUrlView(APIView):
    # TODO Restringir
    permission_classes = [IsAuthenticated]

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
        print("ip", request.META.get('HTTP_X_FORWARDED_FOR'))
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

        # Si no se proporciona una ubicación en la solicitud, asigna una ubicación por defecto.
        if not ubicacion_data:
            nueva_ubicacion = obtener_ubicacion(request)
            ubicacion = Ubicacion.objects.filter(latitud=nueva_ubicacion["latitud"], longitud=nueva_ubicacion["longitud"]).first()

            if not ubicacion:
                ubicacion_serialiazer = UbicacionSerializer(data=nueva_ubicacion)
                if ubicacion_serialiazer.is_valid():
                    ubicacion = ubicacion_serialiazer.save()
                else:
                    print("Error al guardar la nueva ubicacion en la BD")
                    print(ubicacion_serialiazer.errors)
                    ubicacion = Ubicacion.objects.filter(nombre="Ubicación no disponible").first()

        else:
            print("detecto ubicacion")

            # Extraer latitud y longitud de los datos proporcionados.(Agregar valor defecto por si no llega alguno)
            latitud = ubicacion_data.get('latitud')
            longitud = ubicacion_data.get('longitud')

            latitud_normalizada = round(Decimal(str(latitud)),6)
            longitud_normalizada = round(Decimal(str(longitud)), 6)

            print(f"Lat de la request {latitud_normalizada} Long de la reque: {longitud_normalizada}")

            # Buscar en la base de datos si ya existe una ubicación con la misma latitud y longitud.
            ubicacion = Ubicacion.objects.filter(latitud=latitud_normalizada, longitud=longitud_normalizada).first()

            # Si la ubicación no existe en la base de datos
            if not ubicacion:
                print("Creando en ubicacion en BD")
                # Llamar a la funcion que asigna nombre a la ubicacion por su latitud y longitud
                ubicacion_nombre = get_location_name(latitud_normalizada, longitud_normalizada)

                # Variable que contiene los datos de la nueva ubicacion a guardar en BD
                nueva_ubicacion = {
                    "nombre" : ubicacion_nombre,
                    "latitud" : latitud_normalizada,
                    "longitud" : longitud_normalizada
                }

                ubicacion_serialiazer = UbicacionSerializer(data=nueva_ubicacion)
                if ubicacion_serialiazer.is_valid():
                    ubicacion = ubicacion_serialiazer.save()
                else:
                    print("Error al guardar la nueva ubicacion en la BD")
                    print(ubicacion_serialiazer.errors)
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

# Vista que genera datos de analisis estadistico
class StatisticsAnalysisView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):

        # Verificar que el usuario tenga busquedas
        usuario = request.user
        if not usuario.busquedas.exists():
            return Response({
                "error" : "El usuario no tiene búsquedas registradas"
            }, status=status.HTTP_404_NOT_FOUND)

        # Obtener las busquedas del usuario autenticado
        busquedas = Busqueda.objects.filter(usuario=request.user)

        # Convertir los datos en una lista de diccionarios
        data = list(busquedas.values("fecha_creacion","enfermedad","ubicacion","usuario"))

        # Convertir en un DataFrame
        data_frame = pd.DataFrame(data)
        #print(data_frame)

        # LLamar funciones de analisis
        # Variable que almacena resultados de la funcion que encuentra la moda en un periodo de 30 dias
        datos_moda_30d = encontrar_moda(data_frame)

        # Buscar nombre enfermedad en la BD y asignarla a la clave enfermedad del diccionario
        datos_moda_30d["enfermedad"] = _((Enfermedad.objects.filter(id=datos_moda_30d["enfermedad"]).first()).nombre)

        #Si no encuentra la enfermedad
        if len(datos_moda_30d["enfermedad"]) <= 0:
            return Response({
                "error" : "Enfermedad No encontrada"
            }, status=status.HTTP_404_NOT_FOUND)

        # Moda ubicaciones
        datos_moda_ubicaciones = encontrar_moda_ubicacion(data_frame)

        for item in datos_moda_ubicaciones:
            # Buscar nombre ubicacion en la BD y asignarla a la clave ubicacion del diccionario
            item['ubicacion'] = (Ubicacion.objects.filter(id=item['ubicacion']).first()).nombre

            #Si no encuentra la enfermedad
            if len(item['ubicacion']) <= 0:
                return Response({
                    "error" : "Ubicacion No encontrada"
                }, status=status.HTTP_404_NOT_FOUND)

            # Buscar nombre enfermedad en la BD y asignarla a la clave enfermedad del diccionario
            item['enfermedad'] = _((Enfermedad.objects.filter(id=item['enfermedad']).first()).nombre)

            #Si no encuentra la enfermedad
            if len(item['enfermedad']) <= 0:
                return Response({
                    "error" : "Enfermedad No encontrada"
                }, status=status.HTTP_404_NOT_FOUND)   

        datos_conteo_enfermedades = contar_plantas_por_salud(data_frame)
        conteo_registros_dict = {}

        for clave in datos_conteo_enfermedades.keys():
            clave_nombre =_((Enfermedad.objects.filter(id=clave).first()).nombre)

            #Si no encuentra la enfermedad
            conteo_registros_dict[clave_nombre] = datos_conteo_enfermedades[clave]
            if len(item['enfermedad']) <= 0:
                return Response({
                    "error" : "Enfermedad No encontrada"
                }, status=status.HTTP_404_NOT_FOUND) 

        return Response({
            "estadisticas" : {
                "frecuencia_por_fecha" : datos_moda_30d,
                "frecuencia_por_ubicacion" : datos_moda_ubicaciones,
                "conteo_enfermedades" : conteo_registros_dict
            }
        })
