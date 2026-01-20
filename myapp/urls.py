from django.urls import path
from .views import registro_visita
from myapp.views import backup_database
from . import views
from .views import obtener_registro, editar_registro, eliminar_seleccionados
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # URLs principales
    path('', views.vista_inicio, name='vista_inicio'),
    path('inicio/', views.vista_inicio, name='vista_inicio_alternativo'),
    path('redirigir/', views.redirigir_por_tipo_usuario, name='redirigir_usuario'),
    
    # URLs de gestión de visitas (CRUD)
    path('visitas/', views.registro_visita, name='lista_registros'),
    path('visitas/registro/', views.formulario, name='registro_visita'),  # Para crear nuevo
    path('visitas/obtener/<int:id_registro>/', views.obtener_registro, name='obtener_registro'),
    path('visitas/editar/<int:id_registro>/', views.editar_registro, name='editar_registro'),
    path('visitas/eliminar/<int:id_registro>/', views.eliminar_registro, name='eliminar_registro'),
    path('visitas/eliminar-seleccionados/', views.eliminar_seleccionados, name='eliminar_seleccionados'),
    
    # URLs de formulario (alias para compatibilidad)
    path('formulario/', views.formulario, name='formulario'),
    
    # URLs de mapas y geolocalización
    path('mapa/', views.mapa, name='mapa'),
    
    # URLs de respaldo
    path('backup/', views.backup_database, name='backup_database'),
    
    # URLs de gráficas y estadísticas
    path('estadistica/', views.graficos_indicadores, name='estadistica'),
    path('vista_graficas/', views.vista_graficas, name='vista_graficas'),
    
    
    
    path('panel/', views.panel_documentos, name='panel_documentos'),
    path('panel/subir/', views.subir_documento, name='subir_documento'),
    path('panel/editar/<int:id>/', views.editar_documento, name='editar_documento'),
    path('panel/eliminar/<int:id>/', views.eliminar_documento, name='eliminar_documento'),
    # Repositorio público
    path('repositorio/', views.repositorio_publico, name='repositorio'),
    path('repositorio-publico/', views.repositorio_publico, name='repositorio_publico'),
    path('descargar/<int:id>/', views.descargar_documento, name='descargar_documento'),
    path('detalle/<int:id>/', views.ver_documento_detalle, name='detalle_documento'),
    
    # Estadísticas y exportación
    path('estadisticas/', views.obtener_estadisticas, name='estadisticas'),
    path('exportar/csv/', views.exportar_documentos_csv, name='exportar_csv'),
       path('lista/', views.panel_documentos, name='lista_documentos'), 
    # Versión con clases (opcional)
    path('clase/', views.DocumentoListView.as_view(), name='panel_documentos_clase'),
    


    
    path('registros/', views.registro_visita, name='lista_registros'),  # Cambia 'registro' a 'lista_registros' si es necesario
    path('registros/crear/', views.formulario, name='crear_registro'),  # Nueva URL para crear registro
    path('registros/<int:id_registro>/', views.obtener_registro, name='obtener_registro'),
    path('registros/editar/<int:id_registro>/', views.editar_registro, name='editar_registro'),
    path('registros/eliminar/<int:id_registro>/', views.eliminar_registro, name='eliminar_registro'),
    
     path('registro/', views.formulario, name='registro'),  # Opción 1: usar 'formulario' como 'registro'
    # O
    path('registro/', views.registro_visita, name='registro'),
        
        
        
  
    path('subir-url/', views.subir_desde_url, name='subir_desde_url'),

    path('archivos/detalle/<int:archivo_id>/', views.detalle_archivo, name='detalle_archivo'),
    path('archivos/editar/<int:archivo_id>/', views.editar_archivo, name='editar_archivo'),
    path('lista-archivos/', views.lista_archivos, name='lista_archivos'),
    path('toggle-visibilidad/<int:archivo_id>/', views.toggle_visibilidad, name='toggle_visibilidad'),
    
    
    path('procesar/<int:archivo_id>/', views.procesar_archivo, name='procesar_archivo'),
    
    
    
    path('actualizar-url/<int:archivo_id>/', views.actualizar_desde_url, name='actualizar_desde_url'),
    path('eliminar/<int:archivo_id>/', views.eliminar_archivo, name='eliminar_archivo'),
    path('crear-categoria/', views.crear_categoria, name='crear_categoria'),
    # Verificación masiva
    path('verificar-urls/', views.verificar_urls, name='verificar_urls'),
    path('archivos/api/categorias/', views.get_categorias_json, name='get_categorias_json'),
    
]