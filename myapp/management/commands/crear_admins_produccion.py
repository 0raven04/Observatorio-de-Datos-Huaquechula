from django.core.management.base import BaseCommand
from django.db import transaction, connection
from myapp.models import Usuario, Administrador, Encuestador

class Command(BaseCommand):
    help = 'Crea o actualiza los 3 administradores del proyecto (Edgar, Kevin, Brayan) con acceso total'

    def handle(self, *args, **options):
        admins = [
            {
                'nombre': 'Edgar',
                'ap': 'Morales',
                'nombre_usuario': 'edgar',
                'email': 'edgar@observatorio-huaquechula.mx',
                'password': 'Edgar#Admin2026!',
            },
            {
                'nombre': 'Kevin',
                'ap': 'Vázquez',
                'nombre_usuario': 'kevin',
                'email': 'kevin@observatorio-huaquechula.mx',
                'password': 'Kevin#Admin2026!',
            },
            {
                'nombre': 'Brayan',
                'ap': 'Ramos',
                'nombre_usuario': 'brayan',
                'email': 'brayan@observatorio-huaquechula.mx',
                'password': 'Brayan#Admin2026!',
            }
        ]

        with transaction.atomic():
            for item in admins:
                user = Usuario.objects.filter(nombre_usuario=item['nombre_usuario']).first()
                if not user:
                    user = Usuario(
                        nombre_usuario=item['nombre_usuario'],
                        email=item['email'],
                        nombre=item['nombre'],
                        ap=item['ap'],
                        am='',
                        tipo='admin',
                        is_staff=True,
                        is_superuser=True,
                        is_active=True
                    )
                    user.set_password(item['password'])
                    user.save()
                    self.stdout.write(self.style.SUCCESS(f"Usuario {item['nombre_usuario']} CREADO."))
                else:
                    user.nombre = item['nombre']
                    user.ap = item['ap']
                    user.email = item['email']
                    user.tipo = 'admin'
                    user.is_staff = True
                    user.is_superuser = True
                    user.is_active = True
                    user.set_password(item['password'])
                    user.save()
                    self.stdout.write(self.style.SUCCESS(f"Usuario {item['nombre_usuario']} ACTUALIZADO."))

                # Perfil Administrador
                try:
                    admin_prof, created = Administrador.objects.get_or_create(id_usuario=user)
                    self.stdout.write(f"Perfil Administrador: {admin_prof} (creado={created})")
                except Exception as e:
                    self.stdout.write(f"Nota Administrador: {e}")
                    try:
                        with connection.cursor() as cursor:
                            cursor.execute('INSERT INTO "Administrador" (id_usuario, clave_admin) VALUES (%s, %s) ON CONFLICT DO NOTHING', [user.id_usuario, f"ADM_{user.id_usuario}"])
                    except Exception as e2:
                        self.stdout.write(f"Fallback Administrador: {e2}")

                # Perfil Encuestador
                enc_prof, enc_created = Encuestador.objects.get_or_create(id_usuario=user)
                self.stdout.write(f"Perfil Encuestador clave {enc_prof.clave_encuestador} (creado={enc_created})")

        self.stdout.write(self.style.SUCCESS("=== 3 ADMINISTRADORES CONFIGURADOS CON ÉXITO ==="))
