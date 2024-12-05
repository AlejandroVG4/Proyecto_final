from django.db import models


# Create your models here.

class Tratamiento(models.Model):
    nombre = models.CharField(max_length=255)
    descripcion = models.TextField()
    fuente = models.URLField()  # Nueva columna para almacenar la fuente (URL)
    
    def __str__(self):
        return self.nombre
    
class Enfermedad(models.Model):
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField()
    tratamientos = models.ManyToManyField(Tratamiento, related_name="enfermedades")

    def __str__(self):
        return self.nombre    
