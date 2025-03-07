from django.http import JsonResponse
from rest_framework.response import Response
import requests
from .getIp import obtener_ip
from rest_framework import status

dict_ubicacion_defecto = {
            "nombre": "Ubicación no disponible",
            "latitud": 0.000000,
            "longitud": 0.000000
        }

def obtener_ubicacion(request):
    try:
        ip = obtener_ip(request)
        # ip = "179.1.217.252"

        if not ip or ip == "127.0.0.1":
            return dict_ubicacion_defecto

        url = f"http://ip-api.com/json/{ip}"
        respuesta = requests.get(url, timeout=5).json()

        if respuesta.get("status") == "fail":
            return dict_ubicacion_defecto

        dict_respuesta = {
            "nombre": respuesta["city"],
            "latitud": respuesta["lat"],
            "longitud": respuesta["lon"]
        }   
        
        return dict_respuesta

    except (requests.RequestException, KeyError):
        return dict_ubicacion_defecto