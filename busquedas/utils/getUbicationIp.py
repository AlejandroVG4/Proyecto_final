from django.http import JsonResponse
import requests
from .getIp import obtener_ip
from rest_framework import status

def obtener_ubicacion(request):
    try:
        ip = obtener_ip(request)

        if not ip or ip == "127.0.0.1":
            return JsonResponse({"error": "No se puede obtener ubicación en localhost"}, status=status.HTTP_400_BAD_REQUEST)

        url = f"http://ip-api.com/json/{ip}"
        respuesta = requests.get(url, timeout=5).json()

        if respuesta.get("status") == "fail":
            return JsonResponse({"error": "No se pudo obtener la ubicación"}, status=status.HTTP_400_BAD_REQUEST)

        dict_respuesta = {
            "nombre": respuesta["city"],
            "latitud": respuesta["lat"],
            "longitud": respuesta["lon"]
        }   
        
        return dict_respuesta

    except (requests.RequestException, KeyError):
        return JsonResponse({"error": "Error al obtener la ubicación"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)