from django.contrib.auth.models import BaseUserManager


class UserManager(BaseUserManager):
    """
    Un gestor de usuarios personalizado para crear y gestionar usuarios y superusuarios.

    Esta clase hereda de `BaseUserManager` y proporciona métodos personalizados para crear usuarios
    normales y superusuarios. Los métodos aseguraran que los correos estén normalizados y que las
    contraseñas se encripten correctamente antes de guardar a los usuarios en la base de datos.

    Métodos disponibles:
        - create_user: Crea un usuario normal con correo y contraseña.
        - create_superuser: Crea un superusuario con privilegios administrativos.
    """

    # Especificamos que este manager debe ser considerado durante las migraciones
    use_in_migrations = True

    # Metodo para crear un usuario normal

    def create_user(self, email, password, **extra_fields):

        """
        Crea y devuelve un usuario con un correo y contraseña especificados.
        
        :param email: El correo electrónico del usuario.
        :param password: La contraseña del usuario.
        :param extra_fields: Campos adicionales como nombre, etc.
        :return: El objeto usuario creado.
        """
        if not email:
            raise ValueError('Correo Requerido')
        
        if not password:
            raise ValueError('Contraseña Requerida')
        
        # Crea el objeto de usuario
        user = self.model(email=self.normalize_email(email), **extra_fields)

        # - `self.model` hace referencia al modelo de usuario (por ejemplo, `User().create_user`).
        # - `normalize_email` es un método de `BaseUserManager` que asegura que el correo esté en un formato estándar.
        # - `extra_fields` es un diccionario de campos adicionales que se pueden pasar al crear un usuario.
        # - `normalize_email` solo normaliza el dominio del correo electrónico.

        # Encriptar la contraseña 
        user.set_password(password)

        # Guarda el usuario en la base de datos
        user.save(using=self.db)

        return user
    
    # NOTE: Metodo para crear un superusuario con privilegios de administrador
    def create_superuser(self, email, password, **extra_fields):

        """
        Crea y devuelve un superusuario con permisos de administración.
        
        :param email: El correo electrónico del superusuario.
        :param password: La contraseña del superusuario.
        :param extra_fields: Campos adicionales como nombre, etc.
        :return: El objeto superusuario creado.
        """

        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('el atributo is_staff debe ser True')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('el atributo is_superuser debe ser True')
        
        return self.create_user(email, password, **extra_fields)