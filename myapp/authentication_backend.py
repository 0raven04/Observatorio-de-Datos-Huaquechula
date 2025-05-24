from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.hashers import check_password
from myapp.models import Usuario
from django.contrib.auth.models import User

class UsuarioBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None):
        try:
            usuario = Usuario.objects.get(nombre_usuario=username)
            if check_password(password, usuario.contrasenia):
                user, created = User.objects.get_or_create(
                    username=usuario.nombre_usuario,
                    defaults={
                        'is_staff': usuario.tipo == 'admin',
                        'is_superuser': usuario.tipo == 'admin'
                    }
                )
                return user
        except Usuario.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None