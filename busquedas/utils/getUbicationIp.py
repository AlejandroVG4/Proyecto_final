import requests
from .getIp import obtener_ip

def obtener_ubicacion(request):
    ip = obtener_ip(request)

    if ip == "127.0.0.1":
        return JsonResponse({"error": "No se puede obtener ubicación en localhost"})

    url = f"http://ip-api.com/json/{ip}"
    respuesta = requests.get(url).json()
    
    dict_respuesta = {
        "nombre": respuesta["city"],
        "latitud": respuesta["lat"],
        "longitud": respuesta["lon"]
    }
    print(dict_respuesta)
    return dict_respuesta
