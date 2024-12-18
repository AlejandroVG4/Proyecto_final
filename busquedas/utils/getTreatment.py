from enfermedades.models import Enfermedad, Tratamiento
from enfermedades.serializers import TratamientoSerializer
import random

def get_treatment(illness):
    print("En funcion get_treatment")
    
    try:
        # Verificar si el resultado es healthy
        if illness == "healthy":
             # Cuando la planta este sana no entregar tratamiento
            return {"mensaje" : "La planta está sana y no requiere tratamiento"}
        
        # Obtiene la enfermedad
        illness_bd = Enfermedad.objects.get(nombre=illness)

        # Filtrar los tratamientos de esa enfermedad
        treatments = Tratamiento.objects.filter(enfermedad_id=illness_bd.pk)

        # convertir a un diccionario
        serializer = TratamientoSerializer(treatments, many = True)

        # Asignar uno al azar
        tratamiento = random.choice(serializer.data)

        #Diccionario con pk y diccionario de tratamiento
        diccionario_chill = {"illness_pk" : illness_bd.pk , "tratamiento" : tratamiento}

        return diccionario_chill
    except Enfermedad.DoesNotExist:
        # Manejar error cuando la enfermedad que entregue la ia no exista
        return {"error": f"Tratamientos para esta enfermedad: {illness} no disponibles "}


    
    