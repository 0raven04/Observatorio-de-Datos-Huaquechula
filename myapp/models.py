from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User 
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.hashers import check_password
import django.utils.timezone


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
            return None# Modelos del Observatorio Territorial

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
    unidad_medida = models.CharField(max_length=50, blank=True)
    
    # Campos para integración con INEGI
    inegi_indicator_id = models.CharField(max_length=50, blank=True, null=True, help_text="ID del indicador en la API del INEGI")
    data_source = models.CharField(max_length=20, default='manual', choices=[
        ('manual', 'Manual'),
        ('inegi', 'INEGI'),
        ('encuesta', 'Encuesta'),
        ('other', 'Otra fuente')
    ])
    geo_code = models.CharField(max_length=10, default='21071', help_text="Código geográfico de INEGI (ej. 21071 Huaquechula, 21 Puebla, 00 Nacional)")
    NIVEL_CHOICES = [
        ('municipal', 'Municipal'),
        ('estado', 'Estatal'),
        ('nacional', 'Nacional'),
    ]
    nivel_geografico = models.CharField(max_length=10, choices=NIVEL_CHOICES, default='municipal', help_text="Nivel geográfico del indicador: municipal, estatal o nacional")
    last_sync = models.DateTimeField(null=True, blank=True, help_text="Última sincronización con fuente externa")

    # Campos para integración con Encuestas del Observatorio
    encuesta_tipo = models.CharField(max_length=50, blank=True, null=True, choices=[
        ('institucional', 'Institucional'),
        ('visitante', 'Visitante/Turista'),
        ('residente', 'Residente')
    ], help_text="Tipo de encuesta que alimenta el indicador")
    encuesta_pregunta = models.CharField(max_length=100, blank=True, null=True, help_text="Pregunta(s) específica(s) de la encuesta")

    def __str__(self):
        return self.nombre

class Medicion(models.Model):
    indicador = models.ForeignKey(Indicador, on_delete=models.CASCADE, related_name='mediciones')
    periodo = models.CharField(max_length=50)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_registro = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.indicador.nombre} ({self.periodo}): {self.valor}"


# --- NUEVOS MODELOS DE ENCUESTAS (ALIMENTACIÓN MANUAL DEL OBSERVATORIO) ---

class EncuestaResidente(models.Model):
    fecha = models.DateTimeField(auto_now_add=True)
    encuestador = models.ForeignKey(Encuestador, on_delete=models.SET_NULL, null=True, blank=True)
    edad = models.PositiveSmallIntegerField(
        verbose_name='Edad',
        validators=[MinValueValidator(0), MaxValueValidator(127)]
    )
    GENERO_CHOICES = [('Hombre', 'Hombre'), ('Mujer', 'Mujer'), ('Otro', 'Otro')]
    genero = models.CharField(max_length=15, choices=GENERO_CHOICES, verbose_name='Género')
    barrio_colonia = models.CharField(max_length=100, verbose_name='Barrio / Colonia')

    # ── Bloque A: Eje de Tradición y Patrimonio ──────────────────────────
    P1_CHOICES = [
        (1, 'No altera nada'),
        (2, 'Altera poco'),
        (3, 'Altera de forma regular'),
        (4, 'Altera mucho'),
    ]
    alteracion_rutina = models.PositiveSmallIntegerField(
        choices=P1_CHOICES,
        verbose_name='1. ¿Qué tanto considera que la afluencia de visitantes altera negativamente su rutina diaria durante las festividades?'
    )

    P2_CHOICES = [
        (1, 'Excelente (Los servicios operan con normalidad)'),
        (2, 'Regular (Se nota escasez o retrasos temporales)'),
        (3, 'Deficiente (Hay cortes de servicios o fallas graves debido al turismo)'),
    ]
    acceso_servicios_festividades = models.PositiveSmallIntegerField(
        choices=P2_CHOICES,
        verbose_name='2. ¿Cómo califica el acceso y disponibilidad de servicios públicos durante las temporadas festivas?'
    )

    P3_CHOICES = [
        (1, 'Sí, se ha comercializado excesivamente y pierde su esencia comunitaria'),
        (2, 'Parcialmente, conviven la tradición y el comercio de forma equilibrada'),
        (3, 'No, la tradición se mantiene intacta y fuerte'),
    ]
    desvirtuacion_tradicion = models.PositiveSmallIntegerField(
        choices=P3_CHOICES,
        verbose_name='3. ¿Considera que el turismo ha provocado cambios que desvirtúan el significado original de nuestras tradiciones?'
    )

    P4_CHOICES = [
        (1, 'Sí, participo activamente de manera directa'),
        (2, 'No participo directamente, pero apoyo la organización local'),
        (3, 'No participo en absoluto'),
    ]
    participacion_preservacion = models.PositiveSmallIntegerField(
        choices=P4_CHOICES,
        verbose_name='4. ¿Participa usted de forma activa en actividades de preservación (artesanías, cocina tradicional, altares monumentales)?'
    )

    # ── Bloque B: Eje de Turismo de Base Comunitaria (TBC) ───────────────
    P5_CHOICES = [
        (1, 'Sí, asisto con regularidad y se toman en cuenta mis opiniones'),
        (2, 'He sido convocado, pero no asisto o no se toman en cuenta las opiniones'),
        (3, 'Nunca he sido convocado ni informado sobre estas decisiones'),
    ]
    participacion_decisiones = models.PositiveSmallIntegerField(
        choices=P5_CHOICES,
        verbose_name='5. ¿Ha participado o ha sido convocado a reuniones para decidir cómo debe gestionarse el turismo en su localidad?'
    )

    P6_CHOICES = [
        (1, 'Sí, he recibido capacitación continua'),
        (2, 'Recibí información aislada, pero no capacitación formal'),
        (3, 'No he recibido ninguna información ni capacitación'),
    ]
    capacitacion_turistica = models.PositiveSmallIntegerField(
        choices=P6_CHOICES,
        verbose_name='6. ¿Ha recibido capacitación o información clara sobre cómo emprender o atender al turismo de manera responsable?'
    )

    P7_CHOICES = [
        (1, 'Sí, es nuestra fuente de ingresos principal'),
        (2, 'Sí, funciona como una actividad económica complementaria'),
        (3, 'No, no percibimos ningún beneficio directo de la actividad turística'),
    ]
    beneficio_economico = models.PositiveSmallIntegerField(
        choices=P7_CHOICES,
        verbose_name='7. ¿Su hogar percibe un beneficio económico o social directo derivado de algún proyecto turístico local?'
    )

    P8_CHOICES = [
        (1, 'Sí, de forma activa: Existe un fuerte interés y los jóvenes participan activamente en el aprendizaje y preservación de la tradición.'),
        (2, 'Parcialmente: Conocen las tradiciones y participan en las festividades, pero se está perdiendo la enseñanza de las técnicas o significados profundos.'),
        (3, 'No, se está perdiendo: Debido a la migración u otros factores, los jóvenes ya no están aprendiendo estos saberes comunitarios.'),
    ]
    interes_jovenes = models.PositiveSmallIntegerField(
        choices=P8_CHOICES,
        verbose_name='8. En su hogar o entorno cercano, ¿las generaciones más jóvenes (niños y jóvenes) muestran interés y están aprendiendo activamente los saberes, técnicas y significados de nuestras tradiciones (como la elaboración de altares, artesanías o cocina tradicional)?',
        blank=True, null=True
    )

    def __str__(self):
        return f"Encuesta Residente {self.id} - {self.fecha.strftime('%Y-%m-%d')}"


class EncuestaInstitucional(models.Model):
    fecha = models.DateTimeField(auto_now_add=True)
    encuestador = models.ForeignKey(Encuestador, on_delete=models.SET_NULL, null=True, blank=True)

    # ── Bloque A: Eje de Tradición y Patrimonio ──────────────────────────
    P1_CHOICES = [
        (1, 'Sí, contamos con herramientas de monitoreo e inventarios sistemáticos'),
        (2, 'Se realizan registros eventuales (fotografías o bitácoras de eventos), pero sin un sistema formal'),
        (3, 'No se cuenta con herramientas institucionales de seguimiento'),
    ]
    registro_pci = models.PositiveSmallIntegerField(
        choices=P1_CHOICES,
        verbose_name='1. ¿Cuenta la administración municipal actual con registros, inventarios actualizados o indicadores formales para dar seguimiento periódico al estado de conservación del Patrimonio Cultural Inmaterial (PCI) del municipio?'
    )

    canales_difusion = models.JSONField(
        blank=True, default=list,
        verbose_name='2. ¿Cuáles son los canales oficiales y mecanismos institucionales implementados en el último año para la difusión nacional e internacional del PCI de Huaquechula?'
    )

    # ── Bloque B: Eje de Turismo de Base Comunitaria (TBC) ───────────────
    P3_CHOICES = [
        (1, 'Reglamento de turismo vigente que incluye normativas de protección local y ordenamiento comercial'),
        (2, 'Normas básicas de comercio, pero sin un reglamento específico orientado a la protección cultural'),
        (3, 'No existen herramientas de regulación turística vigentes'),
    ]
    mecanismos_regulacion = models.PositiveSmallIntegerField(
        choices=P3_CHOICES,
        verbose_name='3. ¿Qué mecanismos normativos o reglamentos locales posee el ayuntamiento para regular el flujo turístico, evitar la saturación de los espacios públicos y proteger los derechos de los artesanos y portadores de identidad?'
    )

    P4_CHOICES = [
        (1, 'Sí, se cuenta con un Plan Sectorial alineado a la gestión comunitaria'),
        (2, 'Existe un plan de desarrollo general, pero carece de un enfoque específico en turismo comunitario'),
        (3, 'No se cuenta con herramientas de planeación técnica o estratégica en turismo'),
    ]
    plan_desarrollo = models.PositiveSmallIntegerField(
        choices=P4_CHOICES,
        verbose_name='4. ¿Dispone el municipio de un Plan de Desarrollo Turístico Municipal u otras herramientas de gestión técnica que prioricen la participación social de las comunidades rurales anfitrionas?'
    )

    P5_CHOICES = [
        (1, 'Menos del 25% de las localidades (La actividad se centraliza casi por completo en la cabecera municipal)'),
        (2, 'Entre el 25% y el 50% de las localidades están integradas'),
        (3, 'Más del 50% de las localidades rurales participan activamente en las redes de turismo municipal'),
    ]
    porcentaje_comunidades = models.PositiveSmallIntegerField(
        choices=P5_CHOICES,
        verbose_name='5. ¿Qué porcentaje de las comunidades rurales con vocación turística del municipio están integradas activamente en los corredores o proyectos turísticos oficiales promovidos por el ayuntamiento?'
    )

    # Nuevas preguntas agregadas por requerimiento del usuario
    visitantes_ano = models.PositiveIntegerField(
        verbose_name='Número de visitantes registrados al municipio durante el año',
        blank=True, null=True
    )
    visitantes_tradicion = models.PositiveIntegerField(
        verbose_name='Número de visitantes registrados al municipio durante la tradición',
        blank=True, null=True
    )

    def __str__(self):
        return f"Encuesta Institucional {self.id} - {self.fecha.strftime('%Y-%m-%d')}"


class EncuestaVisitante(models.Model):
    fecha = models.DateTimeField(auto_now_add=True)
    encuestador = models.ForeignKey(Encuestador, on_delete=models.SET_NULL, null=True, blank=True)

    # I. Perfil del Visitante
    GENERO_CHOICES = [
        ('femenino', 'Femenino'),
        ('masculino', 'Masculino'),
        ('no_binario', 'No binario / Otro'),
        ('prefiero_no_decir', 'Prefiero no decirlo'),
    ]
    genero = models.CharField(max_length=20, choices=GENERO_CHOICES, verbose_name='¿Con qué género te identificas?')
    edad = models.PositiveSmallIntegerField(
        verbose_name='¿Cuál es tu edad?',
        validators=[MinValueValidator(0), MaxValueValidator(127)]
    )

    GRUPO_VIAJE_CHOICES = [
        ('solo', 'Solo / Sola'),
        ('pareja', 'En pareja'),
        ('familia_ninos', 'En familia (con niños)'),
        ('amigos_adultos', 'Con amigos / familiares (adultos)'),
        ('grupo_organizado', 'Grupo organizado / Excursión'),
    ]
    grupo_viaje = models.CharField(max_length=20, choices=GRUPO_VIAJE_CHOICES, verbose_name='¿Con quién viajas en este viaje?')

    # II. Origen y Conectividad
    ciudad_origen = models.CharField(max_length=100, verbose_name='Ciudad de residencia')
    estado_origen = models.CharField(max_length=100, verbose_name='Estado / Provincia')
    pais_origen = models.CharField(max_length=100, default='México', verbose_name='País')

    ZONAS_CHOICES = [
        ('centro', 'Centro'),
        ('altares', 'Altares monumentales'),
        ('ex_convento', 'Ex Convento Franciscano de San Martín Caballero'),
        ('paramo', 'Páramo de los Duendes'),
        ('acueducto', 'Acueducto de Matlala'),
        ('piedras', 'La Piedra Máscara, La Piedra del Coyote y La Piedra del Sol y la Luna'),
    ]
    zonas_visitadas = models.JSONField(default=list, blank=True, verbose_name='Zonas visitadas o por visitar')

    # III. Comportamiento y Actividades
    ACTIVIDADES_CHOICES = [
        ('gastronomia', 'Probar la gastronomía local / ir a restaurantes'),
        ('sitios_historicos', 'Visitar museos, iglesias o sitios históricos'),
        ('artesanias', 'Comprar artesanías o productos locales'),
        ('naturaleza', 'Actividades de naturaleza / senderismo / aventura'),
        ('evento_festival', 'Asistir a un evento, fiesta patronal o festival tradicional'),
        ('negocios', 'Turismo de negocios / congresos'),
        ('descanso', 'Descanso / Relajación'),
    ]
    actividades = models.JSONField(default=list, blank=True, verbose_name='¿Qué actividades realizaste durante tu estancia?')

    # IV. Satisfacción y Reseñas
    calificacion = models.PositiveSmallIntegerField(
        choices=[
            (1, '⭐ Muy mala'),
            (2, '⭐⭐ Mala'),
            (3, '⭐⭐⭐ Regular'),
            (4, '⭐⭐⭐⭐ Buena'),
            (5, '⭐⭐⭐⭐⭐ Excelente'),
        ],
        verbose_name='¿Cómo calificarías tu experiencia en nuestro municipio?'
    )
    comentario = models.TextField(blank=True, verbose_name='¿Qué fue lo que más te gustó de tu visita?')

    def __str__(self):
        return f"Encuesta Visitante {self.id} - {self.ciudad_origen} - {self.fecha.strftime('%Y-%m-%d')}"


class Categoria_Sitio(models.Model):
    id_categoria = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100, unique=True)
    codigo_slug = models.CharField(max_length=50, unique=True)
    
    class Meta:
        db_table = 'Categoria_Sitio'
        verbose_name = 'Categoría de Sitio'
        verbose_name_plural = 'Categorías de Sitios'
        ordering = ['nombre']

class ArchivoKMZ(models.Model):
    id_archivo = models.AutoField(primary_key=True)
    nombre_archivo = models.CharField(max_length=255)
    archivo_path = models.URLField(max_length=1000, blank=True, null=True, verbose_name='URL del archivo')
    descripcion = models.TextField(blank=True, null=True)
    tamanio = models.BigIntegerField(default=0)
    hash_archivo = models.CharField(max_length=64, blank=True, null=True)
    TIPO_CHOICES = [
        ('kml', 'KML (Archivo geográfico)'),
        ('kmz', 'KMZ (Archivo comprimido)'),
        ('imagen', 'Imagen (JPG, PNG, GIF, etc.)'),
        ('video', 'Video (MP4, AVI, etc.)'),
        ('audio', 'Audio (MP3, WAV, etc.)'),
        ('pdf', 'Documento PDF'),
        ('otro', 'Otro tipo de archivo'),
    ]
    tipo_archivo = models.CharField(max_length=10, choices=TIPO_CHOICES, default='kmz')
    procesado = models.BooleanField(default=False)
    error_procesamiento = models.TextField(blank=True, null=True)
    fecha_subida = models.DateTimeField(default=django.utils.timezone.now)
    procesado_en = models.DateTimeField(blank=True, null=True)
    visible = models.BooleanField(default=True)
    url_disponible = models.BooleanField(default=True, verbose_name='URL disponible')
    ultima_verificacion_url = models.DateTimeField(blank=True, null=True)
    codigo_respuesta_url = models.IntegerField(blank=True, null=True)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, db_column='usuario_id')
    
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

class Documento(models.Model):
    id_documento = models.AutoField(primary_key=True)
    titulo = models.CharField(max_length=200)
    fecha_carga = models.DateTimeField(default=django.utils.timezone.now)
    descripcion = models.TextField(blank=True, null=True)
    url = models.TextField(blank=True, default='')
    fecha_actualizacion = models.DateTimeField(blank=True, null=True)
    CLASIFICACION_CHOICES = [
        ('publico', 'Público'),
        ('privado', 'Privado'),
        ('confidencial', 'Confidencial'),
    ]
    clasificacion = models.CharField(max_length=13, choices=CLASIFICACION_CHOICES, default='publico')
    clave_admin = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, db_column='clave_admin')
    
    class Meta:
        db_table = 'Documento'
        verbose_name = 'Documento'
        verbose_name_plural = 'Documentos'
        ordering = ['-fecha_carga']

class GeometriaEspacial(models.Model):
    id_geometria = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=255, blank=True, null=True)
    TIPO_CHOICES = [
        ('punto', 'Punto'),
        ('linea', 'Línea'),
        ('poligono', 'Polígono'),
        ('multipoligono', 'Multipolígono'),
        ('multipunto', 'Multipunto'),
    ]
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    coordenadas = models.JSONField()
    propiedades = models.JSONField(blank=True, null=True)
    estilo = models.JSONField(blank=True, null=True)
    perimetro = models.DecimalField(max_digits=15, decimal_places=6, blank=True, null=True)
    area = models.DecimalField(max_digits=15, decimal_places=6, blank=True, null=True)
    fecha_creacion = models.DateTimeField(default=django.utils.timezone.now)
    id_archivo = models.ForeignKey(ArchivoKMZ, on_delete=models.CASCADE, blank=True, null=True, db_column='id_archivo')
    
    class Meta:
        db_table = 'GeometriaEspacial'
        verbose_name = 'Geometría Espacial'
        verbose_name_plural = 'Geometrías Espaciales'
        indexes = [
            models.Index(fields=['id_archivo', 'tipo']),
            models.Index(fields=['tipo']),
        ]

class Punto_Interes(models.Model):
    id_punto = models.AutoField(primary_key=True)
    CATEGORIA_CHOICES = [
        ('ofrenda', 'Ofrenda'),
        ('servicio', 'Servicio'),
        ('sitio_turistico', 'Sitio Turístico'),
        ('evento', 'Evento'),
        ('otro', 'Otro'),
    ]
    categoria = models.CharField(max_length=20, choices=CATEGORIA_CHOICES)
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    imagen_portada = models.URLField(max_length=500, blank=True, null=True, verbose_name='URL de imagen portada')
    ESTADO_CHOICES = [
        ('activo', 'Activo'),
        ('inactivo', 'Inactivo'),
    ]
    estado = models.CharField(max_length=10, choices=ESTADO_CHOICES, default='activo')
    fecha_inicio = models.DateField(blank=True, null=True)
    fecha_fin = models.DateField(blank=True, null=True)
    hora_apertura = models.TimeField(blank=True, null=True)
    hora_cierre = models.TimeField(blank=True, null=True)
    dias_semana = models.CharField(max_length=100, blank=True, null=True)
    fecha_registro = models.DateTimeField(default=django.utils.timezone.now)
    id_geometria = models.ForeignKey(GeometriaEspacial, on_delete=models.SET_NULL, blank=True, null=True, db_column='id_geometria')
    usuario_creacion = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, db_column='usuario_creacion')
    
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

class Ofrenda(models.Model):
    id_ofrenda = models.AutoField(primary_key=True)
    anfitrion = models.CharField(max_length=100)
    id_punto = models.OneToOneField(Punto_Interes, on_delete=models.CASCADE, db_column='id_punto')
    
    class Meta:
        db_table = 'Ofrenda'
        verbose_name = 'Ofrenda'
        verbose_name_plural = 'Ofrendas'

class Galeria_Multimedia(models.Model):
    id_foto = models.AutoField(primary_key=True)
    url_archivo = models.URLField(max_length=1000, verbose_name='URL del archivo')
    TIPO_CHOICES = [
        ('imagen', 'Imagen'),
        ('video', 'Video'),
        ('audio', 'Audio'),
    ]
    tipo_archivo = models.CharField(max_length=10, choices=TIPO_CHOICES, default='imagen')
    descripcion = models.TextField(blank=True, null=True)
    es_portada = models.BooleanField(default=False)
    fecha_subida = models.DateTimeField(default=django.utils.timezone.now)
    id_punto = models.ForeignKey(Punto_Interes, on_delete=models.CASCADE, db_column='id_punto')
    
    class Meta:
        db_table = 'Galeria_Multimedia'
        verbose_name = 'Multimedia'
        verbose_name_plural = 'Galería Multimedia'
        ordering = ['-es_portada', '-fecha_subida']

class Ruta(models.Model):
    id_ruta = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    duracion_estimada = models.IntegerField(default=0, help_text='Duración en minutos')
    longitud_km = models.DecimalField(max_digits=8, decimal_places=2, default=0.0)
    DIFICULTAD_CHOICES = [
        ('facil', 'Fácil'),
        ('moderada', 'Moderada'),
        ('dificil', 'Difícil'),
    ]
    dificultad = models.CharField(max_length=10, choices=DIFICULTAD_CHOICES, default='moderada')
    ESTADO_CHOICES = [
        ('activa', 'Activa'),
        ('inactiva', 'Inactiva'),
    ]
    estado = models.CharField(max_length=10, choices=ESTADO_CHOICES, default='activa')
    clave_propietario = models.ForeignKey(User, on_delete=models.CASCADE, db_column='clave_propietario', default=1)
    id_geometria = models.ForeignKey(GeometriaEspacial, on_delete=models.SET_NULL, blank=True, null=True, db_column='id_geometria')

class Ruta_Detalle(models.Model):
    id_ruta_detalle = models.AutoField(primary_key=True)
    orden = models.IntegerField()
    tiempo_parada = models.IntegerField(blank=True, null=True, help_text='Tiempo en minutos')
    actividad_sugerida = models.TextField(blank=True, null=True)
    id_punto = models.ForeignKey(Punto_Interes, on_delete=models.CASCADE, db_column='id_punto')
    id_ruta = models.ForeignKey(Ruta, on_delete=models.CASCADE, db_column='id_ruta')
    
    class Meta:
        db_table = 'Ruta_Detalle'
        verbose_name = 'Detalle de Ruta'
        verbose_name_plural = 'Detalles de Ruta'
        ordering = ['id_ruta', 'orden']
        unique_together = [['id_ruta', 'orden']]

class Servicio(models.Model):
    id_servicio = models.AutoField(primary_key=True)
    TIPO_CHOICES = [
        ('cajero', 'Cajero'),
        ('hospedaje', 'Hospedaje'),
        ('modulo', 'Módulo'),
        ('salud', 'Salud'),
        ('transporte', 'Transporte'),
    ]
    tipo_servicio = models.CharField(max_length=20, choices=TIPO_CHOICES, default='hospedaje')
    contacto = models.CharField(max_length=100, blank=True, null=True)
    tipo_pago = models.CharField(max_length=100, default='efectivo')
    id_punto = models.OneToOneField(Punto_Interes, on_delete=models.CASCADE, db_column='id_punto')
    
    class Meta:
        db_table = 'Servicio'
        verbose_name = 'Servicio'
        verbose_name_plural = 'Servicios'

class Sitio_turistico(models.Model):
    id_sitio = models.AutoField(primary_key=True)
    reglas_acceso = models.TextField(blank=True, null=True)
    id_categoria = models.ForeignKey(Categoria_Sitio, on_delete=models.CASCADE, db_column='id_categoria')
    id_punto = models.OneToOneField(Punto_Interes, on_delete=models.CASCADE, db_column='id_punto')
    
    class Meta:
        db_table = 'Sitio_turistico'
        verbose_name = 'Sitio Turístico'
        verbose_name_plural = 'Sitios Turísticos'

class Propietario(models.Model):
    clave_propietario = models.AutoField(primary_key=True)
    id_usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, db_column='id_usuario', related_name='propietario')
    
    class Meta:
        db_table = 'Propietario'

class Administrador(models.Model):
    clave_admin = models.AutoField(primary_key=True)
    id_usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, db_column='id_usuario', related_name='administrador')
    
    class Meta:
        db_table = 'Administrador'

class ResenaGlobal(models.Model):
    id_resena = models.AutoField(primary_key=True)
    nombre_visitante = models.CharField(max_length=100, blank=True, null=True)
    calificacion = models.PositiveSmallIntegerField()
    comentario = models.TextField(blank=True, null=True)
    fecha_publicacion = models.DateTimeField(auto_now_add=True)
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('aprobada', 'Aprobada'),
        ('oculta', 'Oculta'),
    ]
    estado = models.CharField(max_length=10, choices=ESTADO_CHOICES, default='aprobada')
    likes = models.PositiveIntegerField(default=0)
    ip_visitante = models.GenericIPAddressField(blank=True, null=True)
    id_usuario = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, db_column='id_usuario', related_name='resenas')
    
    class Meta:
        db_table = 'Resena_Global'
        verbose_name = 'Reseña Global'
        verbose_name_plural = 'Reseñas Globales'
        ordering = ['-fecha_publicacion']

