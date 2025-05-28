from django.db import models
from django.contrib.auth.models import User 
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.hashers import check_password


class Usuario(models.Model):
    id_usuario = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=50)
    ap = models.CharField(max_length=50)
    am = models.CharField(max_length=50)
    nombre_usuario = models.CharField(max_length=50, unique=True)
    email = models.EmailField(unique=True)
    contrasenia = models.CharField(max_length=255)
    TIPO_CHOICES = [
        ('admin', 'Admin'),
        ('encuestador', 'Encuestador'),
        ('propietario', 'Propietario'),
    ]
    tipo = models.CharField(max_length=12, choices=TIPO_CHOICES)

    def __str__(self):
        return self.nombre_usuario
    

    class Meta:
        db_table = 'Usuario'  # usa tabla existente con ese nombre


class Encuestador(models.Model):
    # clave_encuestador ES la PK
    clave_encuestador = models.CharField(
        max_length=50,
        primary_key=True,
        db_column='clave_encuestador'
    )

    # relación 1‑a‑1 con Usuario
    id_usuario = models.OneToOneField(
        Usuario,
        on_delete=models.CASCADE,
        db_column='id_usuario',   # ← exactamente como esté en la tabla
        related_name='encuestador'
    )

    def __str__(self):
        return f"{self.clave_encuestador}"
    
    class Meta:
        db_table = 'Encuestador'

class RegistroVisita(models.Model):
    id_registro = models.AutoField(primary_key=True)
    fecha = models.DateField(auto_now_add=True)
    tamanio_grupo = models.PositiveSmallIntegerField(default=1)
    es_extranjero = models.BooleanField(default=False)
    pais_origen = models.CharField(max_length=100, blank=True)
    procedencia = models.CharField(max_length=50, blank=True)

    tipo_transporte_choices = [
        ('Automovil', 'Automovil'),
        ('Autobus', 'Autobus'),
        ('Avion', 'Avion'),
        ('Otro', 'Otro'),
    ]
    tipo_transporte = models.CharField(
        max_length=10,
        choices=tipo_transporte_choices,
        null=True,
        blank=True
    )

    motivo_visita_choices = [
        ('Turismo', 'Turismo'),
        ('Trabajo', 'Trabajo'),
        ('Estudios', 'Estudios'),
        ('Evento', 'Evento'),
        ('Otro', 'Otro'),
    ]
    motivo_visita = models.CharField(
        max_length=20,
        choices=motivo_visita_choices,
        null=True,
        blank=True
    )

    estancia_dias = models.PositiveSmallIntegerField(default=1)
    numero_visitas = models.PositiveSmallIntegerField(default=1)

    id_encuestador = models.ForeignKey(
        Encuestador,
        on_delete=models.CASCADE,
        db_column='id_encuestador',
        to_field='clave_encuestador'
    )

    def __str__(self):
        return f'Registro {self.id_registro} - Encuestador {self.id_encuestador}'

    class Meta:
        db_table = 'Registro_visita'



class PersonaVisita(models.Model):
    id_persona = models.AutoField(primary_key=True)
    id_registro = models.ForeignKey(
        RegistroVisita,
        on_delete=models.CASCADE,
        db_column='id_registro',
        related_name='personas_visita'
    )
    edad = models.PositiveSmallIntegerField()
    sexo_choices = [
        ('Hombre', 'Hombre'),
        ('Mujer', 'Mujer'),
        ('Otro', 'Otro'),
    ]
    sexo = models.CharField(max_length=10, choices=sexo_choices)

    def __str__(self):
        return f'Persona {self.id_persona} - Registro {self.id_registro.id_registro}'

    class Meta:
        db_table = 'Persona_visita'

class UsuarioBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            # Busca el usuario en tu modelo personalizado por nombre_usuario
            usuario = Usuario.objects.get(nombre_usuario=username)
            # Verifica la contraseña, si usas hash
            # Si guardas contraseña en texto plano (no recomendado), cambia esto
            if check_password(password, usuario.contrasenia):  # cambio según cómo guardes la contraseña
                # Crear o devolver un objeto User para la sesión de Django
                # Lo usamos para que Django admin y login funcionen
                user, created = User.objects.get_or_create(username=usuario.nombre_usuario)
                return user
        except Usuario.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
        
