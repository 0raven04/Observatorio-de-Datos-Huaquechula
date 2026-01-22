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
    path('repositorio/', views.repositorio, name='repositorio'),
    path('estadistica/', views.graficos_indicadores, name='estadistica'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    # path('graficas-ejemplo/', views.graficas_ejemplo, name='graficas_ejemplo'),  # Temporalmente comentado
    path('api/indicator/<int:indicator_id>/chart-data/', views.indicator_chart_data, name='indicator_chart_data'),

    
    # JSON-stat endpoints
    path('api/indicator/<int:indicator_id>/jsonstat/', views.indicator_jsonstat_data, name='indicator_jsonstat'),
    path('api/compare-municipalities/', views.compare_municipalities_view, name='compare_municipalities'),
]

