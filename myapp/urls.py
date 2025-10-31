from django.urls import path
from .views import registro_visita
from myapp.views import backup_database
from . import views
from .views import obtener_registro, editar_registro, eliminar_seleccionados
from django.conf import settings
from django.conf.urls.static import static


# Definición de patrones URL para la aplicación
urlpatterns = [
    # URL para realizar respaldo de la base de datos
    path('backup/', views.backup_database, name='backup_database'),
    # URL principal para el listado de registros de visitas
    path('visitas/', views.registro_visita, name='lista_registros'),
    # URL para obtener datos de un registro específico (formato JSON)
    path('visitas/obtener/<int:id_registro>/', obtener_registro, name='obtener_registro'),
    # URL para procesar la edición de un registro existente
    path('visitas/editar/<int:id_registro>/', editar_registro, name='editar_registro'),
    # URL para eliminar un registro individual
    path('visitas/eliminar/<int:id_registro>/', views.eliminar_registro, name='eliminar_registro'),
    # URL para eliminar múltiples registros seleccionados
    path('visitas/eliminar-seleccionados/', eliminar_seleccionados, name='eliminar_seleccionados'),
    path('inicio/', views.vista_inicio, name='vista_inicio'),
    path('vista_graficas/', views.vista_graficas, name='vista_graficas'),
    path('redirigir/', views.redirigir_por_tipo_usuario, name='redirigir_usuario'),
    path('formulario/', views.formulario, name='formulario'),
    path('registro/', views.formulario, name='registro'),
    path("mapa/", views.mapa, name="mapa"),
    path('', views.vista_inicio, name='vista_inicio'),
    path('subir-documento/', views.subir_documento, name='subir_documento'),
    path('descargar/<int:documento_id>/', views.descargar_documento, name='descargar_documento'),
    path('eliminar/<int:documento_id>/', views.eliminar_documento, name='eliminar_documento'),
    path('api/documentos/<str:categoria_id>/', views.obtener_documentos_categoria, name='documentos_categoria'),
    path('repositorio/', views.repositorio, name='repositorio'),
    path('estadistica/', views.graficos_indicadores, name='estadistica'),
]