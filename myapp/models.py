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
        db_table = 'Usuario'  

class Encuestador(models.Model):
    # clave_encuestador ES la PK
    clave_encuestador = models.CharField(
        max_length=50,
        primary_key=True,
        db_column='clave_encuestador'
    )

    id_usuario = models.OneToOneField(
        Usuario,
        on_delete=models.CASCADE,
        db_column='id_usuario',   
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
        return f"Persona en Visita {self.id_registro.id_registro} - Edad: {self.edad}, Sexo: {self.sexo}"

    class Meta:
        db_table = 'Persona_visita'


class UsuarioBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            usuario = Usuario.objects.get(nombre_usuario=username)
            if check_password(password, usuario.contrasenia):  
                user, created = User.objects.get_or_create(username=usuario.nombre_usuario)
                return user
        except Usuario.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

class Lugar(models.Model):
    nombre = models.CharField(max_length=100)
    latitud = models.FloatField()
    longitud = models.FloatField()

    def __str__(self):
        return self.nombre
    
#prueba 
# models.py
from django.db import models
from django.utils import timezone

class Categoria(models.Model):
    nombre = models.CharField(max_length=100)
    icono = models.CharField(max_length=50, default='fas fa-folder')
    orden = models.IntegerField(default=0)
    
    class Meta:
        verbose_name_plural = "Categorías"
        ordering = ['orden', 'nombre']
    
    def __str__(self):
        return self.nombre
    
    def contar_documentos(self):
        return self.documento_set.count()

class Documento(models.Model):
    titulo = models.CharField(max_length=255)
    descripcion = models.TextField(blank=True, null=True)
    archivo = models.FileField(upload_to='documentos/%Y/%m/')
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, related_name='documentos')
    fecha_subida = models.DateTimeField(default=timezone.now)
    tamaño = models.IntegerField(default=0)  # en bytes
    tipo_archivo = models.CharField(max_length=10, blank=True)
    es_publico = models.BooleanField(default=True)
    descargas = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['-fecha_subida']
        verbose_name_plural = "Documentos"
    
    def __str__(self):
        return self.titulo
    
    def save(self, *args, **kwargs):
        if self.archivo:
            self.tipo_archivo = self.archivo.name.split('.')[-1].lower()
            self.tamaño = self.archivo.size
        super().save(*args, **kwargs)
    
    def tamaño_formateado(self):
        """Retorna el tamaño en formato legible"""
        bytes = self.tamaño
        if bytes == 0:
            return '0 Bytes'
        k = 1024
        sizes = ['Bytes', 'KB', 'MB', 'GB']
        i = 0
        while bytes >= k and i < len(sizes) - 1:
            bytes /= k
            i += 1
        return f"{bytes:.2f} {sizes[i]}"
    
    def es_video(self):
        return self.tipo_archivo in ['mp4', 'avi', 'mov', 'wmv', 'mkv']
    
    def es_imagen(self):
        return self.tipo_archivo in ['jpg', 'jpeg', 'png', 'gif', 'bmp']
    
    def es_pdf(self):
        return self.tipo_archivo == 'pdf'
    
    def icono_archivo(self):
        """Retorna el ícono FontAwesome apropiado"""
        if self.es_video():
            return 'fas fa-file-video'
        elif self.es_imagen():
            return 'fas fa-file-image'
        elif self.es_pdf():
            return 'fas fa-file-pdf'
        elif self.tipo_archivo in ['doc', 'docx']:
            return 'fas fa-file-word'
        elif self.tipo_archivo in ['xls', 'xlsx']:
            return 'fas fa-file-excel'
        elif self.tipo_archivo in ['ppt', 'pptx']:
            return 'fas fa-file-powerpoint'
        else:
            return 'fas fa-file'

# Modelos del Observatorio Territorial

class Eje(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)

    def __str__(self):
        return self.nombre

class CategoriaIndicador(models.Model):
    eje = models.ForeignKey(Eje, on_delete=models.CASCADE, related_name='categorias')
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.eje.nombre} - {self.nombre}"

class Indicador(models.Model):
    categoria = models.ForeignKey(CategoriaIndicador, on_delete=models.CASCADE, related_name='indicadores')
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    unidad_medida = models.CharField(max_length=50, blank=True) # e.g., "Porcentaje", "Años", "Cantidad"
    
    # Campos para integración con INEGI
    inegi_indicator_id = models.CharField(max_length=50, blank=True, null=True, help_text="ID del indicador en la API del INEGI")
    data_source = models.CharField(max_length=20, default='manual', choices=[
        ('manual', 'Manual'),
        ('inegi', 'INEGI'),
        ('other', 'Otra fuente')
    ])
    last_sync = models.DateTimeField(null=True, blank=True, help_text="Última sincronización con fuente externa")

    def __str__(self):
        return self.nombre

class Medicion(models.Model):
    indicador = models.ForeignKey(Indicador, on_delete=models.CASCADE, related_name='mediciones')
    periodo = models.CharField(max_length=50) # e.g., "2024", "2024-Q1"
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_registro = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.indicador.nombre} ({self.periodo}): {self.valor}"
# --- NUEVOS MODELOS DE ENCUESTAS (ALIMENTACIÓN MANUAL DEL OBSERVATORIO) ---

class EncuestaResidente(models.Model):
    fecha = models.DateTimeField(auto_now_add=True)
    encuestador = models.ForeignKey(Encuestador, on_delete=models.SET_NULL, null=True, blank=True)
    edad = models.PositiveSmallIntegerField()
    genero_choices = [('Hombre', 'Hombre'), ('Mujer', 'Mujer'), ('Otro', 'Otro')]
    genero = models.CharField(max_length=15, choices=genero_choices)
    barrio_colonia = models.CharField(max_length=100)
    
    # Seguridad
    confianza_policia = models.PositiveSmallIntegerField(choices=[(1,'1 - Nula'), (2,'2 - Poca'), (3,'3 - Regular'), (4,'4 - Mucha'), (5,'5 - Total')], verbose_name='Confianza en la policía (1-5)')
    percepcion_inseguridad = models.PositiveSmallIntegerField(choices=[(1,'Muy inseguro'), (2,'Inseguro'), (3,'Neutral'), (4,'Seguro'), (5,'Muy seguro')], verbose_name='Percepción de inseguridad')
    
    # Tradiciones / PCI
    tension_festividades = models.PositiveSmallIntegerField(choices=[(1,'Siempre'), (2,'Frecuentemente'), (3,'A veces'), (4,'Rara vez'), (5,'Nunca')], verbose_name='¿Siente tensión por exceso de visitantes en festividades?')
    acceso_servicios_festividades = models.PositiveSmallIntegerField(choices=[(1,'Muy afectado'), (2,'Moderadamente'), (3,'Poco'), (4,'Nada')], verbose_name='¿Se ve afectado su acceso a servicios (agua, tránsito) en festividades?')
    perdida_tradicion = models.PositiveSmallIntegerField(choices=[(1,'Totalmente de acuerdo'), (2,'De acuerdo'), (3,'Neutral'), (4,'En desacuerdo'), (5,'Totalmente en desacuerdo')], verbose_name='¿Se está perdiendo el respeto a la tradición por el turismo?')
    
    # Medio Ambiente
    calidad_aire = models.PositiveSmallIntegerField(choices=[(1,'Ha empeorado'), (2,'Se mantiene igual'), (3,'Ha mejorado mucho')], verbose_name='Percepción de la calidad del aire')
    gestion_residuos = models.PositiveSmallIntegerField(choices=[(1,'Deficiente'), (2,'Regular'), (3,'Excelente')], verbose_name='Percepción de la gestión de residuos')

    def __str__(self):
        return f"Encuesta Residente {self.id} - {self.fecha.strftime('%Y-%m-%d')}"


class EncuestaComercio(models.Model):
    fecha = models.DateTimeField(auto_now_add=True)
    encuestador = models.ForeignKey(Encuestador, on_delete=models.SET_NULL, null=True, blank=True)
    tipo_comercio_choices = [('Hospedaje', 'Hospedaje'), ('Alimentos', 'Alimentos'), ('Artesanía', 'Taller/Artesanía'), ('Guía', 'Guía turístico'), ('Otro', 'Otro')]
    tipo_comercio = models.CharField(max_length=50, choices=tipo_comercio_choices)
    
    # Gobernanza y Turismo
    participacion_decisiones = models.PositiveSmallIntegerField(choices=[(1,'No, decisiones unilaterales'), (2,'Rara vez'), (3,'A veces, ciertos grupos'), (4,'Sí, siempre')], verbose_name='¿Se toma en cuenta a la comunidad local para decisiones turísticas?')
    capacitacion_turistica = models.PositiveSmallIntegerField(choices=[(1,'No he recibido'), (2,'Sí, pero insuficientes'), (3,'Sí, frecuentes y útiles')], verbose_name='¿Ha recibido capacitación para mejorar sus servicios?')
    integracion_turistica = models.PositiveSmallIntegerField(choices=[(1,'Trabajan de forma aislada'), (2,'Parcialmente integrados'), (3,'Muy integrados')], verbose_name='¿Qué tan integrados están los proyectos turísticos locales?')

    def __str__(self):
        return f"Encuesta Comercio {self.id} - {self.tipo_comercio} - {self.fecha.strftime('%Y-%m-%d')}"
