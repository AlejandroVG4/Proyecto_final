from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid


# Create your models here.

class Ubicacion(models.Model):
    nombre = models.CharField(max_length=100)
    latitud = models.DecimalField(max_digits=9, decimal_places=6)
    longitud = models.DecimalField(max_digits=9, decimal_places=6)

    def __str__(self):
        return self.nombre

class Dispositivo(models.Model):
    num_dispositivo = models.IntegerField()
    usuario = models.ForeignKey('usuarios.Usuarios', on_delete=models.CASCADE, related_name="dispositivos")

    def __str__(self):
        return f"Dispositivo {self.num_dispositivo} de {self.usuario.email}"

class Usuarios(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(("email address"), blank=False, unique=True)
    is_verified = models.BooleanField(default=False)
    fecha_creacion = models.DateTimeField(auto_now_add=True) 
    ubicaciones = models.ManyToManyField(Ubicacion, related_name="usuarios")
    
    def __str__(self):
        return self.email