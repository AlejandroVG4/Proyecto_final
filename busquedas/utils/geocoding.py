from opencage.geocoder import OpenCageGeocode
from gestion_plagas.settings import env
from pprint import pprint

key = env("OPENCAGE_KEY")

def get_location_name(latitude, longitude ):

    try:
        # Importa la clase OpenCageGeocode y crea una instancia con la clave de la API
        geocoder = OpenCageGeocode(key)

        # convierte latitud y longitud en una dirección
        results = geocoder.reverse_geocode(latitude, longitude)

        # TODO si la solicitud falla o no entrega resultados, manejar la excepción
        if not results:
            print("Error: No se encontraron resultados.")
            return None

        # Extrae la dirección completa en formato legible
        formatted_address = results[0].get("formatted")

        if not formatted_address:
            print("Error: Direccion vacía")
            return None

        # Divide la dirección en partes separadas por comas
        parts = formatted_address.split(", ")

        # Obtiene el segundo elemento, que generalmente corresponde al barrio
        location_name = parts[1]

        return location_name
    
    except Exception as e:
        print(f"Error al obtener la ubicación: {e}")
        return None
        