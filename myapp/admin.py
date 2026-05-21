from django.contrib import admin

from .models import (
    Usuario, Encuestador, Propietario, Administrador,
    RegistroVisita,
    Ofrenda, Servicio, Categoria_Sitio, Sitio_turistico, Galeria_Multimedia,
    Ruta, Ruta_Detalle,
    ArchivoKMZ, GeometriaEspacial, Punto_Interes, Documento,
    ResenaGlobal,
)
    


admin.site.register(Usuario)
admin.site.register(Encuestador)
admin.site.register(Propietario)
admin.site.register(Administrador)
admin.site.register(Ofrenda)
admin.site.register(Servicio)
admin.site.register(Sitio_turistico)
admin.site.register(Ruta)
admin.site.register(Ruta_Detalle)
admin.site.register(Galeria_Multimedia)
admin.site.register(ArchivoKMZ)
admin.site.register(GeometriaEspacial)
admin.site.register(Punto_Interes)
admin.site.register(Categoria_Sitio)
admin.site.register(Documento)


@admin.register(RegistroVisita)
class RegistroVisitaAdmin(admin.ModelAdmin):
    list_display = ['id_registro', 'fecha', 'total_personas', 'es_extranjero', 'procedencia', 'motivo_visita', 'clave_encuestador']
    list_filter = ['es_extranjero', 'motivo_visita', 'tipo_transporte', 'fecha']
    search_fields = ['procedencia', 'pais_origen', 'clave_encuestador__clave_encuestador']
    readonly_fields = ['fecha', 'total_personas']
    date_hierarchy = 'fecha'
    
    fieldsets = (
        ('Información básica', {
            'fields': ('fecha', 'estancia_dias', 'motivo_visita', 'tipo_transporte')
        }),
        ('Origen de los visitantes', {
            'fields': ('procedencia', 'es_extranjero', 'pais_origen')
        }),
        ('Distribución por edad y género - Mujeres', {
            'fields': (
                ('mujeres_0_15', 'mujeres_16_30', 'mujeres_31_45'),
                ('mujeres_46_60', 'mujeres_61_75', 'mujeres_76_mas'),
            ),
            'classes': ('collapse',)
        }),
        ('Distribución por edad y género - Hombres', {
            'fields': (
                ('hombres_0_15', 'hombres_16_30', 'hombres_31_45'),
                ('hombres_46_60', 'hombres_61_75', 'hombres_76_mas'),
            ),
            'classes': ('collapse',)
        }),
        ('Encuestador', {
            'fields': ('clave_encuestador',)
        }),
        ('Resumen', {
            'fields': ('total_personas',),
            'classes': ('wide',)
        }),
    )
    
    def total_personas(self, obj):
        return obj.total_personas
    total_personas.short_description = 'Total de Personas'
    



class DocumentoAdmin(admin.ModelAdmin):
    list_display = ['id_documento', 'titulo', 'get_clasificacion_display', 'fecha_carga', 'fecha_actualizacion', 'clave_admin']
    list_filter = ['clasificacion', 'fecha_carga']
    search_fields = ['titulo', 'descripcion', 'url']
    readonly_fields = ['id_documento', 'fecha_carga', 'fecha_actualizacion']
    list_per_page = 20
    
    fieldsets = (
        ('Información básica', {
            'fields': ('titulo', 'descripcion', 'url')
        }),
        ('Clasificación y permisos', {
            'fields': ('clasificacion', 'clave_admin'),
            'description': 'Configura quién puede ver este documento'
        }),
        ('Metadatos (automáticos)', {
            'fields': ('fecha_carga', 'fecha_actualizacion'),
            'classes': ('collapse',),
            'description': 'Estos campos se generan automáticamente'
        }),
    )
    
    def get_readonly_fields(self, request, obj=None):
        """Hacer el id_documento solo lectura cuando se edita"""
        if obj:  # Cuando se está editando un objeto existente
            return self.readonly_fields + ('id_documento',)
        return self.readonly_fields
    
    def save_model(self, request, obj, form, change):
        """Asignar automáticamente el administrador actual si no hay uno"""
        if not obj.clave_admin:
            obj.clave_admin = request.user
        if not obj.id_documento:  # Si es nuevo
            from django.db import connection
            with connection.cursor() as cursor:
                cursor.execute("SELECT MAX(id_documento) FROM Documento")
                max_id = cursor.fetchone()[0]
                obj.id_documento = (max_id or 0) + 1
        super().save_model(request, obj, form, change)
        
        

class ArchivoKMZAdmin(admin.ModelAdmin):
    list_display = ('id_archivo', 'nombre_archivo', 'usuario', 'tipo_archivo', 'visible', 'procesado', 'fecha_subida')
    list_filter = ('tipo_archivo', 'visible', 'procesado', 'usuario')
    search_fields = ('nombre_archivo', 'descripcion', 'archivo_path')
    readonly_fields = ('fecha_subida', 'procesado_en', 'ultima_verificacion_url')
    fieldsets = (
        ('Información Básica', {
            'fields': ('nombre_archivo', 'descripcion', 'usuario')
        }),
        ('URL y Tipo', {
            'fields': ('archivo_path', 'tipo_archivo', 'tamanio', 'hash_archivo')
        }),
        ('Estado', {
            'fields': ('visible', 'procesado', 'procesado_en', 'error_procesamiento')
        }),
        ('Información de URL', {
            'fields': ('url_disponible', 'ultima_verificacion_url', 'codigo_respuesta_url')
        }),
        ('Fechas', {
            'fields': ('fecha_subida', 'fecha_inicio', 'fecha_fin')
        }),
    )

class GeometriaEspacialAdmin(admin.ModelAdmin):
    list_display = ('id_geometria', 'nombre', 'tipo', 'id_archivo', 'fecha_creacion')
    list_filter = ('tipo', 'id_archivo')
    search_fields = ('nombre', 'propiedades')
    readonly_fields = ('fecha_creacion',)



class PuntoInteresAdmin(admin.ModelAdmin):
    list_display = ('id_punto', 'nombre', 'categoria', 'estado', 'usuario_creacion', 'fecha_registro')
    list_filter = ('categoria', 'estado', 'usuario_creacion')
    search_fields = ('nombre', 'descripcion')
    fieldsets = (
        ('Información Básica', {
            'fields': ('nombre', 'descripcion', 'categoria', 'estado', 'imagen_portada')
        }),
        ('Geometría', {
            'fields': ('id_geometria',)
        }),
        ('Horarios y Fechas', {
            'fields': ('fecha_inicio', 'fecha_fin', 'hora_apertura', 'hora_cierre', 'dias_semana')
        }),
        ('Auditoría', {
            'fields': ('usuario_creacion', 'fecha_registro')
        }),
    )


class OfrendaAdmin(admin.ModelAdmin):
    list_display = ('id_ofrenda', 'id_punto', 'anfitrion')
    search_fields = ('anfitrion', 'id_punto__nombre')

class ServicioAdmin(admin.ModelAdmin):
    list_display = ('id_servicio', 'id_punto', 'tipo_servicio', 'contacto')
    list_filter = ('tipo_servicio',)
    search_fields = ('contacto', 'id_punto__nombre')

# === CATEGORÍAS DE SITIOS ===\
class CategoriaSitioAdmin(admin.ModelAdmin):
    list_display = ('id_categoria', 'nombre', 'codigo_slug')
    search_fields = ('nombre', 'codigo_slug')

# === SITIOS TURÍSTICOS ===

class SitioTuristicoAdmin(admin.ModelAdmin):
    list_display = ('id_sitio', 'id_punto', 'id_categoria')
    list_filter = ('id_categoria',)
    search_fields = ('id_punto__nombre', 'reglas_acceso')

# === GALERÍA MULTIMEDIA ===

class GaleriaMultimediaAdmin(admin.ModelAdmin):
    list_display = ('id_foto', 'id_punto', 'tipo_archivo', 'es_portada', 'fecha_subida')
    list_filter = ('tipo_archivo', 'es_portada')
    search_fields = ('descripcion', 'url_archivo', 'id_punto__nombre')

# === RUTAS ===

class RutaAdmin(admin.ModelAdmin):
    list_display = ('id_ruta', 'nombre', 'dificultad', 'estado', 'clave_propietario')
    list_filter = ('dificultad', 'estado', 'clave_propietario')
    search_fields = ('nombre', 'descripcion')

# === DETALLES DE RUTA ===

class RutaDetalleAdmin(admin.ModelAdmin):
    list_display = ('id_ruta_detalle', 'id_ruta', 'id_punto', 'orden', 'tiempo_parada')
    list_filter = ('id_ruta',)
    search_fields = ('actividad_sugerida', 'id_punto__nombre')


# =====================================================
# PANEL DE MODERACIÓN DE RESEÑAS
# =====================================================
@admin.register(ResenaGlobal)
class ResenaGlobalAdmin(admin.ModelAdmin):
    list_display  = [
        'id_resena', 'autor_display', 'calificacion_stars',
        'estado', 'fecha_publicacion', 'likes', 'ip_visitante',
        'modelo_label', 'modelo_score'  
    ]
    list_filter   = [
        'estado', 'calificacion', 'fecha_publicacion',
        'modelo_label'                  
    ]
    search_fields = ['nombre_visitante', 'comentario', 'ip_visitante']
    readonly_fields = ['fecha_publicacion', 'ip_visitante', 'likes']
    list_per_page = 30
    date_hierarchy = 'fecha_publicacion'
    actions = ['aprobar_resenas', 'ocultar_resenas', 'marcar_pendiente']

    fieldsets = (
        ('Autor', {
            'fields': ('id_usuario', 'nombre_visitante', 'ip_visitante'),
        }),
        ('Contenido', {
            'fields': ('calificacion', 'comentario'),
        }),
        ('Moderación', {
            'fields': ('estado', 'likes', 'fecha_publicacion'),
        }),
    )

    def autor_display(self, obj):
        return obj.autor
    autor_display.short_description = 'Autor'

    def calificacion_stars(self, obj):
        return '★' * obj.calificacion + '☆' * (5 - obj.calificacion)
    calificacion_stars.short_description = 'Calificación'

    @admin.action(description='✅ Aprobar reseñas seleccionadas')
    def aprobar_resenas(self, request, queryset):
        count = queryset.update(estado='aprobada')
        self.message_user(request, f'{count} reseña(s) aprobada(s).')

    @admin.action(description='🚫 Ocultar reseñas seleccionadas')
    def ocultar_resenas(self, request, queryset):
        count = queryset.update(estado='oculta')
        self.message_user(request, f'{count} reseña(s) ocultada(s).')

    @admin.action(description='🔄 Marcar como pendiente')
    def marcar_pendiente(self, request, queryset):
        count = queryset.update(estado='pendiente')
        self.message_user(request, f'{count} reseña(s) marcada(s) como pendiente.')

