from django.contrib import admin
from .models import RegistroVisita
# Register your models here.

admin.site.register(RegistroVisita)

# admin.py
from django.contrib import admin
from .models import Categoria, Documento

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'icono', 'orden', 'contar_documentos']
    list_editable = ['orden']
    ordering = ['orden', 'nombre']

@admin.register(Documento)
class DocumentoAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'categoria', 'tipo_archivo', 'tamaño_formateado', 'fecha_subida', 'es_publico', 'descargas']
    list_filter = ['categoria', 'tipo_archivo', 'es_publico', 'fecha_subida']
    search_fields = ['titulo', 'descripcion']
    readonly_fields = ['fecha_subida', 'tamaño', 'tipo_archivo', 'descargas']
    list_editable = ['es_publico']
    
    fieldsets = (
        ('Información básica', {
            'fields': ('titulo', 'descripcion', 'categoria', 'archivo')
        }),
        ('Configuración', {
            'fields': ('es_publico',)
        }),
        ('Metadatos (solo lectura)', {
            'fields': ('tipo_archivo', 'tamaño', 'fecha_subida', 'descargas'),
            'classes': ('collapse',)
        }),
    )