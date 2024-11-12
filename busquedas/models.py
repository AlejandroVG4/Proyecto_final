from django.db import models
import uuid
from enfermedades.models import Enfermedad
from usuarios.models import Ubicacion

# Create your models here.

class Imagen(models.Model):
    
    url = models.CharField(max_length=255) 

    def __str__(self):
        return self.url 
    

class Busqueda(models.Model):
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False) 
    fecha_creacion = models.DateTimeField(auto_now_add=True)  
    enfermedad = models.ForeignKey(Enfermedad, on_delete=models.CASCADE)  
    ubicacion = models.ForeignKey(Ubicacion, on_delete=models.CASCADE)  
    imagen = models.ForeignKey(Imagen, on_delete=models.CASCADE) 
    usuario = models.ForeignKey('usuarios.Usuarios', on_delete=models.CASCADE, related_name='busquedas')

    def __str__(self):
        return f"Búsqueda {self.id} - {self.fecha_creacion}"
