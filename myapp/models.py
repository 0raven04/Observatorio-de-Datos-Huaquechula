from django.db import models
from django.contrib.auth.models import User


from django.contrib.auth.hashers import check_password
from django.utils import timezone
import os
import uuid
from django.utils import timezone

from mysite import settings

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

# 1. Definir el Manager (Obligatorio para usuarios personalizados)
class UsuarioManager(BaseUserManager):
    def create_user(self, nombre_usuario, email, password=None, **extra_fields):
        if not email:
            raise ValueError('El usuario debe tener un correo electrónico')
        email = self.normalize_email(email)
        user = self.model(nombre_usuario=nombre_usuario, email=email, **extra_fields)
        # set_password encripta la contraseña automáticamente
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, nombre_usuario, email, password=None, **extra_fields):
        extra_fields.setdefault('tipo', 'admin')
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(nombre_usuario, email, password, **extra_fields)

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin

class Usuario(AbstractBaseUser, PermissionsMixin):
    id_usuario = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    ap = models.CharField(max_length=100)
    am = models.CharField(max_length=100, null=True, blank=True)

    nombre_usuario = models.CharField(max_length=50, unique=True)
    email = models.EmailField(max_length=100, unique=True)

    password = models.CharField(max_length=255, db_column='contrasenia')

    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    tipo = models.CharField(
        max_length=12,
        choices=[
            ('admin', 'Admin'),
            ('encuestador', 'Encuestador'),
            ('propietario', 'Propietario'),
        ]
    )

    fecha_registro = models.DateTimeField(auto_now_add=True)

    objects = UsuarioManager()

    USERNAME_FIELD = 'nombre_usuario'
    REQUIRED_FIELDS = ['email', 'nombre', 'ap']

    class Meta:
        db_table = 'Usuario'

    def __str__(self):
        return self.nombre_usuario


class Encuestador(models.Model):
    clave_encuestador = models.AutoField(primary_key=True)
    id_usuario = models.OneToOneField(
        Usuario,
        on_delete=models.CASCADE,
        db_column='id_usuario',
        related_name='encuestador'
    )
    
    def __str__(self):
        return f"Encuestador {self.clave_encuestador}"
    
    class Meta:
        db_table = 'Encuestador'


class Propietario(models.Model):
    clave_propietario = models.AutoField(primary_key=True)
    id_usuario = models.OneToOneField(
        Usuario,
        on_delete=models.CASCADE,
        db_column='id_usuario',
        related_name='propietario'
    )
    
    class Meta:
        db_table = 'Propietario'


class Administrador(models.Model):
    clave_admin = models.AutoField(primary_key=True)
    id_usuario = models.OneToOneField(
        Usuario,
        on_delete=models.CASCADE,
        db_column='id_usuario',
        related_name='administrador'
    )
    
    class Meta:
        db_table = 'Administrador'


class RegistroVisita(models.Model):
    id_registro = models.AutoField(primary_key=True)
    fecha = models.DateTimeField(auto_now_add=True)
    estancia_dias = models.PositiveSmallIntegerField(default=1)
    visitas_previas = models.PositiveSmallIntegerField(default=1)  # CAMPO AGREGADO
    
    MOTIVO_VISITA_CHOICES = [
        ('turismo', 'Turismo'),
        ('negocios', 'Negocios'),
        ('visita_familiar', 'Visita Familiar'),
        ('estudios', 'Estudios'),
        ('otros', 'Otros'),
    ]
    motivo_visita = models.CharField(
        max_length=20,
        choices=MOTIVO_VISITA_CHOICES,
        default='turismo'
    )
    
    TIPO_TRANSPORTE_CHOICES = [
        ('automovil', 'Automóvil'),
        ('autobus', 'Autobús'),
        ('avion', 'Avión'),
        ('tren', 'Tren'),
        ('otros', 'Otros'),
    ]
    tipo_transporte = models.CharField(
        max_length=10,
        choices=TIPO_TRANSPORTE_CHOICES,
        default='automovil'
    )
    
    procedencia = models.CharField(max_length=100)
    pais_origen = models.CharField(max_length=100, blank=True, null=True)
    es_extranjero = models.BooleanField(default=False)
    clave_encuestador = models.ForeignKey(
        Encuestador,
        on_delete=models.RESTRICT,
        db_column='clave_encuestador'
    )
    
    # Campos de distribución por edad y género
    mujeres_0_15 = models.PositiveSmallIntegerField(default=0)
    mujeres_16_30 = models.PositiveSmallIntegerField(default=0)
    mujeres_31_45 = models.PositiveSmallIntegerField(default=0)
    mujeres_46_60 = models.PositiveSmallIntegerField(default=0)
    mujeres_61_75 = models.PositiveSmallIntegerField(default=0)
    mujeres_76_mas = models.PositiveSmallIntegerField(default=0)
    
    hombres_0_15 = models.PositiveSmallIntegerField(default=0)
    hombres_16_30 = models.PositiveSmallIntegerField(default=0)
    hombres_31_45 = models.PositiveSmallIntegerField(default=0)
    hombres_46_60 = models.PositiveSmallIntegerField(default=0)
    hombres_61_75 = models.PositiveSmallIntegerField(default=0)
    hombres_76_mas = models.PositiveSmallIntegerField(default=0)
    
    def __str__(self):
        return f'Registro {self.id_registro} - {self.fecha.strftime("%Y-%m-%d")} - Visitas previas: {self.visitas_previas}'
    
    
    @property
    def total_mujeres(self):
        return (
            self.mujeres_0_15 + self.mujeres_16_30 + self.mujeres_31_45 + 
            self.mujeres_46_60 + self.mujeres_61_75 + self.mujeres_76_mas
        )
    
    @property
    def total_hombres(self):
        return (
            self.hombres_0_15 + self.hombres_16_30 + self.hombres_31_45 + 
            self.hombres_46_60 + self.hombres_61_75 + self.hombres_76_mas
        )
    
    class Meta:
        db_table = 'Registro_visita'
        verbose_name = 'Registro de Visita'
        verbose_name_plural = 'Registros de Visitas'
        ordering = ['-fecha']  # Ordenar por fecha descendente por defecto
    
    @property
    def total_personas(self):
        return (
            self.mujeres_0_15 + self.mujeres_16_30 + self.mujeres_31_45 + 
            self.mujeres_46_60 + self.mujeres_61_75 + self.mujeres_76_mas +
            self.hombres_0_15 + self.hombres_16_30 + self.hombres_31_45 + 
            self.hombres_46_60 + self.hombres_61_75 + self.hombres_76_mas
        )
    
    class Meta:
        db_table = 'Registro_visita'





class Documento(models.Model):
    CLASIFICACION_CHOICES = [
        ('publico', 'Público'),
        ('privado', 'Privado'),
        ('confidencial', 'Confidencial'),
    ]
    TIPO_CHOICES = [
        ('video', 'Video'),
        ('reporte', 'Reporte'),
        ('historico', 'Documento Histórico'),
    ]
    
    id_documento = models.AutoField(primary_key=True)
    titulo = models.CharField(max_length=200)
    fecha_carga = models.DateTimeField(default=timezone.now)
    descripcion = models.TextField(blank=True, null=True)
    
    tipo = models.CharField(
        max_length=20,        # Suficiente para 'historico' o 'video'
        choices=TIPO_CHOICES,
        default='reporte'     # Valor por defecto sugerido
    )
    
    url = models.TextField(
        default='', 
        blank=True,
    )
    
    fecha_actualizacion = models.DateTimeField(null=True, blank=True)
    clasificacion = models.CharField(
        max_length=13,
        choices=CLASIFICACION_CHOICES,
        default='publico'
    )
    clave_admin = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column='clave_admin'
    )
    
    class Meta:
        db_table = 'Documento'
        verbose_name = 'Documento'
        verbose_name_plural = 'Documentos'
        ordering = ['-fecha_carga']
    
    def __str__(self):
        return self.titulo
    
    def save(self, *args, **kwargs):
        if not self.pk:
            self.fecha_carga = timezone.now()
        self.fecha_actualizacion = timezone.now()
        super().save(*args, **kwargs)
    
    @property
    def icono_archivo(self):
        if self.url:
            extension = self.url.split('.')[-1].lower() if '.' in self.url else ''
            iconos = {
                'pdf': 'fas fa-file-pdf',
                'doc': 'fas fa-file-word',
                'docx': 'fas fa-file-word',
                'xls': 'fas fa-file-excel',
                'xlsx': 'fas fa-file-excel',
                'ppt': 'fas fa-file-powerpoint',
                'pptx': 'fas fa-file-powerpoint',
                'jpg': 'fas fa-file-image',
                'jpeg': 'fas fa-file-image',
                'png': 'fas fa-file-image',
                'gif': 'fas fa-file-image',
                'mp4': 'fas fa-file-video',
                'avi': 'fas fa-file-video',
                'mov': 'fas fa-file-video',
                'zip': 'fas fa-file-archive',
                'rar': 'fas fa-file-archive',
                'txt': 'fas fa-file-alt',
            }
            return iconos.get(extension, 'fas fa-file')
        return 'fas fa-file'
    
    @property
    def nombre_clasificacion(self):
        nombres = {
            'publico': 'Público',
            'privado': 'Privado',
            'confidencial': 'Confidencial',
        }
        return nombres.get(self.clasificacion, 'Desconocido')
        
        

#--------------- myapp/kml_processor -------------

class ArchivoKMZ(models.Model):
    # Tipos de archivo compatibles con URLs
    TIPO_ARCHIVO_CHOICES = [
        ('kml', 'KML (Archivo geográfico)'),
        ('kmz', 'KMZ (Archivo comprimido)'),
        ('imagen', 'Imagen (JPG, PNG, GIF, etc.)'),
        ('video', 'Video (MP4, AVI, etc.)'),
        ('audio', 'Audio (MP3, WAV, etc.)'),
        ('pdf', 'Documento PDF'),
        ('otro', 'Otro tipo de archivo'),
    ]
    
    id_archivo = models.AutoField(primary_key=True)
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        db_column='usuario_id'
    )
    nombre_archivo = models.CharField(max_length=255)
    
    # IMPORTANTE: Ahora archivo_path almacena la URL
    archivo_path = models.URLField(max_length=1000, blank=True, null=True, verbose_name="URL del archivo")
    
    descripcion = models.TextField(blank=True, null=True)
    tamanio = models.BigIntegerField(default=0)
    
    # Campo hash para verificar integridad del archivo remoto
    hash_archivo = models.CharField(max_length=64, blank=True, null=True)
    
    # Tipo de archivo extendido
    tipo_archivo = models.CharField(
        max_length=10, 
        choices=TIPO_ARCHIVO_CHOICES,
        default='kmz'
    )
    
    procesado = models.BooleanField(default=False)
    error_procesamiento = models.TextField(blank=True, null=True)
    
    # Fechas de visibilidad
    fecha_subida = models.DateTimeField(default=timezone.now)
    procesado_en = models.DateTimeField(null=True, blank=True)
    
    visible = models.BooleanField(default=True)
    
    # Metadata adicional para URLs
    url_disponible = models.BooleanField(default=True, verbose_name="URL disponible")
    ultima_verificacion_url = models.DateTimeField(null=True, blank=True)
    codigo_respuesta_url = models.IntegerField(null=True, blank=True)
    
    class Meta:
        db_table = 'ArchivoKMZ'
        verbose_name = 'Archivo por URL'
        verbose_name_plural = 'Archivos por URL'
        ordering = ['-fecha_subida']
        indexes = [
            models.Index(fields=['usuario', 'tipo_archivo']),
            models.Index(fields=['visible', 'fecha_subida']),
            models.Index(fields=['procesado']),
        ]
    
    def __str__(self):
        return f"{self.nombre_archivo} ({self.get_tipo_archivo_display()})"
    
    @property
    def usuario_id(self):
        return self.usuario.id if self.usuario else None
    
    @property
    def tamanio_formateado(self):
        """Formatea el tamaño para mostrar al usuario"""
        if self.tamanio == 0:
            return "0 Bytes"
        unidades = ['Bytes', 'KB', 'MB', 'GB', 'TB']
        tamanio = float(self.tamanio)
        for unidad in unidades:
            if tamanio < 1024.0:
                return f"{tamanio:.2f} {unidad}"
            tamanio /= 1024.0
        return f"{tamanio:.2f} TB"
    
    @property
    def esta_visible_ahora(self):
        """Verifica si el archivo debe estar visible ahora"""
        if not self.visible:
            return False
        if not self.url_disponible:
            return False
        return True
    
    @property
    def es_url_valida(self):
        """Verifica si la URL parece válida"""
        return self.archivo_path and (
            self.archivo_path.startswith('http://') or 
            self.archivo_path.startswith('https://')
        )
    
    @property
    def es_archivo_geografico(self):
        """Verifica si es un archivo KML/KMZ"""
        return self.tipo_archivo in ['kml', 'kmz']
    
    @property
    def es_multimedia(self):
        """Verifica si es un archivo multimedia"""
        return self.tipo_archivo in ['imagen', 'video', 'audio']
    
    @property
    def extension_archivo(self):
        """Extrae la extensión del archivo desde la URL"""
        if not self.archivo_path:
            return ''
        url = self.archivo_path.lower()
        if url.endswith('.kml'):
            return '.kml'
        elif url.endswith('.kmz'):
            return '.kmz'
        elif any(url.endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']):
            return 'imagen'
        elif any(url.endswith(ext) for ext in ['.mp4', '.avi', '.mov', '.wmv', '.flv', '.webm']):
            return 'video'
        elif any(url.endswith(ext) for ext in ['.mp3', '.wav', '.ogg', '.flac']):
            return 'audio'
        elif url.endswith('.pdf'):
            return 'pdf'
        return 'otro'
    def obtener_nombre_archivo_url(self):
        """Extrae el nombre del archivo desde la URL"""
        if not self.archivo_path:
            return ''
        return self.archivo_path.split('/')[-1].split('?')[0]

class GeometriaEspacial(models.Model):
    TIPO_GEOMETRIA_CHOICES = [
        ('punto', 'Punto'),
        ('linea', 'Línea'),
        ('poligono', 'Polígono'),
        ('multipoligono', 'Multipolígono'),
        ('multipunto', 'Multipunto'),
    ]  
    id_geometria = models.AutoField(primary_key=True)
    
    # Relación con ArchivoKMZ (puede ser null para geometrías manuales)
    id_archivo = models.ForeignKey(
        ArchivoKMZ,
        on_delete=models.CASCADE,
        db_column='id_archivo',
        null=True,
        blank=True
    )
    nombre = models.CharField(max_length=255, blank=True, null=True)
    tipo = models.CharField(max_length=20, choices=TIPO_GEOMETRIA_CHOICES)
    
    # Almacena las coordenadas en formato JSON
    coordenadas = models.JSONField()
    
    # Centroide para búsquedas espaciales - REMOVER GIS si no lo necesitas
    # centroide = gis_models.PointField(srid=4326, null=True, blank=True)
    
    # Propiedades adicionales del KML/KMZ
    propiedades = models.JSONField(blank=True, null=True)
    
    # Estilo visual
    estilo = models.JSONField(blank=True, null=True)
    
    # Métricas
    perimetro = models.DecimalField(max_digits=15, decimal_places=6, null=True, blank=True)
    area = models.DecimalField(max_digits=15, decimal_places=6, null=True, blank=True)
    
    fecha_creacion = models.DateTimeField(default=timezone.now)
    
    class Meta:
        db_table = 'GeometriaEspacial'
        verbose_name = 'Geometría Espacial'
        verbose_name_plural = 'Geometrías Espaciales'
        indexes = [
            models.Index(fields=['id_archivo', 'tipo']),
            models.Index(fields=['tipo']),
        ]
    
    def __str__(self):
        archivo_nombre = self.id_archivo.nombre_archivo if self.id_archivo else "Manual"
        return f"{self.nombre or 'Sin nombre'} ({self.tipo}) - {archivo_nombre}"
    
    @property
    def es_de_archivo(self):
        """Verifica si la geometría proviene de un archivo"""
        return self.id_archivo is not None
    
    @property
    def tiene_centroide(self):
        """Verifica si tiene centroide calculado"""
        return False  # Cambiar a True si habilitas el campo centroide
    
    @property
    def propiedades_dict(self):
        """Retorna las propiedades como diccionario"""
        return self.propiedades or {}

class Punto_Interes(models.Model):
    CATEGORIA_CHOICES = [
        ('ofrenda', 'Ofrenda'),
        ('servicio', 'Servicio'),
        ('sitio_turistico', 'Sitio Turístico'),
        ('evento', 'Evento'),
        ('otro', 'Otro'),
    ]
    
    ESTADO_CHOICES = [
        ('activo', 'Activo'),
        ('inactivo', 'Inactivo'),
    ]
    
    DIAS_SEMANA = [
        ('lunes', 'Lunes'),
        ('martes', 'Martes'),
        ('miercoles', 'Miércoles'),
        ('jueves', 'Jueves'),
        ('viernes', 'Viernes'),
        ('sabado', 'Sábado'),
        ('domingo', 'Domingo'),
    ]
    
    id_punto = models.AutoField(primary_key=True)
    
    # Relación con geometría (opcional)
    id_geometria = models.ForeignKey(
        GeometriaEspacial,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column='id_geometria'
    )
    
    categoria = models.CharField(max_length=20, choices=CATEGORIA_CHOICES)
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    
    # Imagen de portada (URL)
    imagen_portada = models.URLField(max_length=500, blank=True, null=True, verbose_name="URL de imagen portada")
    
    estado = models.CharField(max_length=10, choices=ESTADO_CHOICES, default='activo')
    
    # Fechas para eventos
    fecha_inicio = models.DateField(null=True, blank=True)
    fecha_fin = models.DateField(null=True, blank=True)
    
    # Horarios
    hora_apertura = models.TimeField(null=True, blank=True)
    hora_cierre = models.TimeField(null=True, blank=True)
    
    # Días de operación
    dias_semana = models.CharField(max_length=100, blank=True, null=True)  # Almacenado como string separado por comas
    
    # Auditoría
    usuario_creacion = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column='usuario_creacion',
        related_name='puntos_creados'
    )
    fecha_registro = models.DateTimeField(default=timezone.now)
    
    class Meta:
        db_table = 'Punto_Interes'
        verbose_name = 'Punto de Interés'
        verbose_name_plural = 'Puntos de Interés'
        ordering = ['nombre']
        indexes = [
            models.Index(fields=['categoria', 'estado']),
            models.Index(fields=['nombre']),
            models.Index(fields=['fecha_inicio', 'fecha_fin']),
        ]
    
    def __str__(self):
        return f"{self.nombre} ({self.get_categoria_display()})"
    
    @property
    def tiene_geometria(self):
        return self.id_geometria is not None
    
    @property
    def esta_activo(self):
        return self.estado == 'activo'
    
    @property
    def es_evento(self):
        return self.categoria == 'evento'
    
    @property
    def dias_semana_list(self):
        """Retorna los días de la semana como lista"""
        if not self.dias_semana:
            return []
        return [dia.strip() for dia in self.dias_semana.split(',')]
    
    @dias_semana_list.setter
    def dias_semana_list(self, value):
        """Establece los días de la semana desde una lista"""
        self.dias_semana = ','.join(value) if value else None

class Ofrenda(models.Model):
    id_ofrenda = models.AutoField(primary_key=True)
    id_punto = models.OneToOneField(
        Punto_Interes,
        on_delete=models.CASCADE,
        db_column='id_punto'
    )
    anfitrion = models.CharField(max_length=100)
    
    class Meta:
        db_table = 'Ofrenda'
        verbose_name = 'Ofrenda'
        verbose_name_plural = 'Ofrendas'
    
    def __str__(self):
        return f"Ofrenda: {self.anfitrion} - {self.id_punto.nombre}"

class Servicio(models.Model):
    TIPO_SERVICIO_CHOICES = [
        ('cajero', 'Cajero'),
        ('hospedaje', 'Hospedaje'),
        ('modulo', 'Módulo'),
        ('salud', 'Salud')
    ]
    
    TIPO_PAGO_CHOICES = [
        ('efectivo', 'Efectivo'),
        ('tarjeta', 'Tarjeta'),
        ('transferencia', 'Transferencia'),
        ('ninguno', 'Ninguno'),
    ]
    
    id_servicio = models.AutoField(primary_key=True)
    id_punto = models.OneToOneField(
        Punto_Interes,
        on_delete=models.CASCADE,
        db_column='id_punto'
    )
    
    # CAMBIO: Agrega valor por defecto
    tipo_servicio = models.CharField(
        max_length=20, 
        choices=TIPO_SERVICIO_CHOICES,
        default='hospedaje'  # ← VALOR POR DEFECTO
    )
    
    contacto = models.CharField(max_length=100, blank=True, null=True)
    
    # Tipo de pago como string separado por comas
    tipo_pago = models.CharField(max_length=100, default='efectivo')
    
    class Meta:
        db_table = 'Servicio'
        verbose_name = 'Servicio'
        verbose_name_plural = 'Servicios'
    
    def __str__(self):
        return f"Servicio {self.get_tipo_servicio_display()}: {self.id_punto.nombre}"

class Categoria_Sitio(models.Model):
    id_categoria = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100, unique=True)
    codigo_slug = models.CharField(max_length=50, unique=True)
    
    class Meta:
        db_table = 'Categoria_Sitio'
        verbose_name = 'Categoría de Sitio'
        verbose_name_plural = 'Categorías de Sitios'
        ordering = ['nombre']
    
    def __str__(self):
        return self.nombre

class Sitio_turistico(models.Model):
    id_sitio = models.AutoField(primary_key=True)
    id_punto = models.OneToOneField(
        Punto_Interes,
        on_delete=models.CASCADE,
        db_column='id_punto'
    )
    id_categoria = models.ForeignKey(
        Categoria_Sitio,
        on_delete=models.CASCADE,
        db_column='id_categoria'
    )
    reglas_acceso = models.TextField(blank=True, null=True)
    
    class Meta:
        db_table = 'Sitio_turistico'
        verbose_name = 'Sitio Turístico'
        verbose_name_plural = 'Sitios Turísticos'
    
    def __str__(self):
        return f"Sitio Turístico: {self.id_punto.nombre}"

class Galeria_Multimedia(models.Model):
    TIPO_ARCHIVO_CHOICES = [
        ('imagen', 'Imagen'),
        ('video', 'Video'),
        ('audio', 'Audio'),
    ]
    
    id_foto = models.AutoField(primary_key=True)
    
    # Relación con Punto de Interés
    id_punto = models.ForeignKey(
        Punto_Interes,
        on_delete=models.CASCADE,
        db_column='id_punto'
    )
    
    # URL del archivo multimedia
    url_archivo = models.URLField(max_length=1000, verbose_name="URL del archivo")
    
    tipo_archivo = models.CharField(max_length=10, choices=TIPO_ARCHIVO_CHOICES, default='imagen')
    descripcion = models.TextField(blank=True, null=True)
    
    es_portada = models.BooleanField(default=False)
    fecha_subida = models.DateTimeField(default=timezone.now)
    
    class Meta:
        db_table = 'Galeria_Multimedia'
        verbose_name = 'Multimedia'
        verbose_name_plural = 'Galería Multimedia'
        ordering = ['-es_portada', '-fecha_subida']
    
    def __str__(self):
        return f"{self.get_tipo_archivo_display()}: {self.url_archivo.split('/')[-1]}"
    
    
    
    

class Ruta(models.Model):
    DIFICULTAD_CHOICES = [
        ('facil', 'Fácil'),
        ('moderada', 'Moderada'),
        ('dificil', 'Difícil'),
    ]
    
    ESTADO_CHOICES = [
        ('activa', 'Activa'),
        ('inactiva', 'Inactiva'),
    ]
    
    id_ruta = models.AutoField(primary_key=True)
    id_geometria = models.ForeignKey(
        GeometriaEspacial,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column='id_geometria'
    )
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    
    # AÑADE VALORES POR DEFECTO
    duracion_estimada = models.IntegerField(
        help_text="Duración en minutos",
        default=0  # ← VALOR POR DEFECTO
    )
    longitud_km = models.DecimalField(
        max_digits=8, 
        decimal_places=2,
        default=0.0  # ← VALOR POR DEFECTO
    )
    dificultad = models.CharField(
        max_length=10, 
        choices=DIFICULTAD_CHOICES, 
        default='moderada'  # ← VALOR POR DEFECTO
    )
    
    # Este campo es problemático - necesita un usuario por defecto
    clave_propietario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        db_column='clave_propietario',
        default=1  # ← ID del usuario por defecto (cambia esto)
    )
    
    estado = models.CharField(
        max_length=10, 
        choices=ESTADO_CHOICES, 
        default='activa'  # ← VALOR POR DEFECTO
    )

class Ruta_Detalle(models.Model):
    id_ruta_detalle = models.AutoField(primary_key=True)
    
    id_ruta = models.ForeignKey(
        Ruta,
        on_delete=models.CASCADE,
        db_column='id_ruta'
    )
    
    id_punto = models.ForeignKey(
        Punto_Interes,
        on_delete=models.CASCADE,
        db_column='id_punto'
    )
    
    orden = models.IntegerField()
    tiempo_parada = models.IntegerField(help_text="Tiempo en minutos", null=True, blank=True)
    actividad_sugerida = models.TextField(blank=True, null=True)
    
    class Meta:
        db_table = 'Ruta_Detalle'
        verbose_name = 'Detalle de Ruta'
        verbose_name_plural = 'Detalles de Ruta'
        ordering = ['id_ruta', 'orden']
        unique_together = ['id_ruta', 'orden']
    
    def __str__(self):
        return f"Ruta {self.id_ruta.nombre} - Punto {self.orden}: {self.id_punto.nombre}"