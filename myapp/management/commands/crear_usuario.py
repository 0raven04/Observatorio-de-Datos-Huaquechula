from django.core.management.base import BaseCommand
from django.db import transaction
from getpass import getpass
from myapp.models import Usuario, Encuestador, Propietario, Administrador

class Command(BaseCommand):
    help = 'Crea un nuevo usuario en el sistema con las relaciones correctas'

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

        # Recolección de datos
        nombre = options['nombre'] or input("Nombre: ")
        ap = options['ap'] or input("Apellido paterno: ")
        am = options['am'] or input("Apellido materno (Enter si no tiene): ")
        nombre_usuario = options['nombre_usuario'] or input("Nombre de usuario: ")
        email = options['email'] or input("Email: ")
        password_plano = options['password'] or getpass("Contraseña: ")
        tipo = options['tipo'] or input("Tipo (admin/encuestador/propietario): ").lower()

        # Validaciones previas
        if Usuario.objects.filter(nombre_usuario=nombre_usuario).exists():
            return self.stdout.write(self.style.ERROR('Error: El nombre de usuario ya existe.'))

        if Usuario.objects.filter(email=email).exists():
            return self.stdout.write(self.style.ERROR('Error: El email ya está registrado.'))

        if tipo not in ['admin', 'encuestador', 'propietario']:
             return self.stdout.write(self.style.ERROR('Error: Tipo de usuario inválido.'))

        try:
            # Usamos transaction.atomic para asegurar que se creen AMBOS (usuario y perfil) o NINGUNO
            with transaction.atomic():
                
                # 1. Crear el Usuario usando el Manager (automáticamente encripta password)
                # Nota: create_user viene del UsuarioManager que definimos antes
                usuario = Usuario.objects.create_user(
                    nombre_usuario=nombre_usuario,
                    email=email,
                    password=password_plano,
                    # Campos extra
                    nombre=nombre,
                    ap=ap,
                    am=am,
                    tipo=tipo
                )

                # 2. Crear el perfil asociado según el tipo
                # NOTA: No pedimos 'clave' porque son AutoField (se generan solas)
                if tipo == 'encuestador':
                    Encuestador.objects.create(id_usuario=usuario)
                    self.stdout.write(f"Perfil de Encuestador creado automáticamente.")

                elif tipo == 'propietario':
                    Propietario.objects.create(id_usuario=usuario)
                    self.stdout.write(f"Perfil de Propietario creado automáticamente.")

                elif tipo == 'admin':
                    Administrador.objects.create(id_usuario=usuario)
                    self.stdout.write(f"Perfil de Administrador creado automáticamente.")

                self.stdout.write(self.style.SUCCESS(f'\n¡ÉXITO! Usuario "{nombre_usuario}" creado correctamente como "{tipo}".'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error al crear usuario: {str(e)}'))