from django.db import models


# Create your models here.
class Enfermedad(models.Model):
    nombre = models.CharField(max_length=200)

    def __str__(self):
        return self.nombre    

class Tratamiento(models.Model):
    descripcion = models.CharField(max_length=255)
    enfermedad = models.ForeignKey(Enfermedad, on_delete=models.CASCADE, related_name="tratamientos")
    fuente = models.URLField(default="urlexample.com")  # Nueva columna para almacenar la fuente (URL)
    
    def __str__(self):
        return self.descripcion
    
