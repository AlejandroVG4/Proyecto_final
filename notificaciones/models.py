from django.db import models
from usuarios.models import Ubicacion

# Create your models here.

class Notificacion(models.Model):
    descripcion = models.CharField(max_length=255)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    ubicacion = models.ForeignKey(Ubicacion, on_delete=models.CASCADE, related_name='notificaciones')

    def __str__(self):
        return f"Notificación {self.id} - {self.descripcion}"


