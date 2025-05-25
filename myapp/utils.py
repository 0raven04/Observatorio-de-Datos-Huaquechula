from django.contrib.auth.hashers import make_password
from myapp.models import Usuario  # Reemplaza 'yourapp' por el nombre real de tu app

def crear_usuario(nombre, ap, am, nombre_usuario, email, password_plano, tipo):
    """
    Crea un nuevo usuario en la base de datos con la contraseña encriptada.
    """
    usuario = Usuario.objects.create(
        nombre=nombre,
        ap=ap,
        am=am,
        nombre_usuario=nombre_usuario,
        email=email,
        contrasenia=make_password(password_plano),
        tipo=tipo
    )
    return usuario
