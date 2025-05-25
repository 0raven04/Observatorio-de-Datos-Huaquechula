from django.contrib.auth.hashers import make_password
from myapp.models import Usuario

def crear_usuario(nombre, ap, am, nombre_usuario, email, password_plano, tipo):
    contrasenia_hash = make_password(password_plano)
    usuario = Usuario(
        nombre=nombre,
        ap=ap,
        am=am,
        nombre_usuario=nombre_usuario,
        email=email,
        contrasenia=contrasenia_hash,
        tipo=tipo
    )
    usuario.save()
    print(f"Usuario {nombre_usuario} creado con contraseña hasheada.")