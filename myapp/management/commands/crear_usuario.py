from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password
from getpass import getpass
from myapp.models import Usuario, Encuestador, Propietario, Administrador

class Command(BaseCommand):
    help = 'Crea un nuevo usuario en el sistema'

    def add_arguments(self, parser):
        parser.add_argument('--nombre', type=str, help='Nombre del usuario')
        parser.add_argument('--ap', type=str, help='Apellido paterno')
        parser.add_argument('--am', type=str, help='Apellido materno')
        parser.add_argument('--nombre_usuario', type=str, help='Nombre de usuario único')
        parser.add_argument('--email', type=str, help='Email del usuario')
        parser.add_argument('--password', type=str, help='Contraseña')
        parser.add_argument('--tipo', type=str, choices=['admin', 'encuestador', 'propietario'], help='Tipo de usuario')

    def handle(self, *args, **options):
        self.stdout.write("\n=== CREACIÓN DE NUEVO USUARIO ===\n")

        nombre = options['nombre'] or input("Nombre: ")
        ap = options['ap'] or input("Apellido paterno: ")
        am = options['am'] or input("Apellido materno: ")
        nombre_usuario = options['nombre_usuario'] or input("Nombre de usuario: ")
        email = options['email'] or input("Email: ")
        password_plano = options['password'] or getpass("Contraseña: ")
        tipo = options['tipo'] or input("Tipo (admin/encuestador/propietario): ").lower()

        # Validaciones
        if Usuario.objects.filter(nombre_usuario=nombre_usuario).exists():
            return self.stdout.write(self.style.ERROR(' El nombre de usuario ya existe'))

        if Usuario.objects.filter(email=email).exists():
            return self.stdout.write(self.style.ERROR(' El email ya está registrado'))

        # Crear usuario
        try:
            usuario = Usuario.objects.create(
                nombre=nombre,
                ap=ap,
                am=am,
                nombre_usuario=nombre_usuario,
                email=email,
                contrasenia=make_password(password_plano),
                tipo=tipo
            )

            if tipo == 'encuestador':
                clave = input("Clave de encuestador: ")
                if Encuestador.objects.filter(clave_encuestador=clave).exists():
                    usuario.delete()
                    return self.stdout.write(self.style.ERROR(' La clave de encuestador ya existe'))

                Encuestador.objects.create(id_usuario=usuario, clave_encuestador=clave)

            elif tipo == 'propietario':
                clave = input("Clave de propietario: ")
                if Propietario.objects.filter(clave_propietario=clave).exists():
                    usuario.delete()
                    return self.stdout.write(self.style.ERROR(' La clave de propietario ya existe'))

                Propietario.objects.create(id_usuario=usuario, clave_propietario=clave)

            elif tipo == 'admin':
                clave = input("Clave de administrador: ")
                if Administrador.objects.filter(clave_admin=clave).exists():
                    usuario.delete()
                    return self.stdout.write(self.style.ERROR(' La clave de administrador ya existe'))

                Administrador.objects.create(id_usuario=usuario, clave_admin=clave)

            self.stdout.write(self.style.SUCCESS(f' Usuario "{nombre_usuario}" creado correctamente como {tipo}'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error al crear usuario: {str(e)}'))
