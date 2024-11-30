from django.db import models
from .managers import UserManager
from django.contrib.auth.models import AbstractBaseUser
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

class Usuarios(AbstractBaseUser):
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=False)
    email = models.EmailField(max_length=100, unique=True, error_messages={'unique' : 'Este Correo electronico ya esta registrado'})
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    # Campo para soft delete
    is_deleted = models.BooleanField(default=False)
    # TODO REVISAR ESTE CAMPO PARA VERIFICACION DE USUARIO DE A TRAVES DEL CORREO
    # is_verified = models.BooleanField(default=False)

    # Indica que utilice el UserManager para interactuar con las instancias del modelo
    objects = UserManager()

    # Indica a django que se usara el email en lugar del username en la autenticacion
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    # Al imprimir el objecto se mostrara el valor de name en lugar de la representacion predeterminada del objeto
    def __str__(self) :
        return self.name

    # Sobre escribir el metodo delete para soft delete
    def delete(self, using=None, keep_parents=False):
        self.is_deleted = True
        self.save(using=using)

    # Metodo para restaurar un usuario
    def restore(self):
        self.is_deleted = False
        self.save()