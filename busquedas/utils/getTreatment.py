from enfermedades.models import Enfermedad, Tratamiento
from enfermedades.serializers import TratamientoSerializer
import random
def get_treatment(illness):
    
    # Filtrar la enfermedad
    illness_bd = Enfermedad.objects.get(nombre=illness)
    print(illness_bd)
    # Filtrar los tratamientos de esa enfermedad
    treatments = Tratamiento.objects.filter(enfermedad_id=illness_bd.pk)

    # convertir a un diccionario
    serializer = TratamientoSerializer(treatments, many = True)

    # Asignar uno al azar
    tratamiento = random.choice(serializer.data)

    return tratamiento