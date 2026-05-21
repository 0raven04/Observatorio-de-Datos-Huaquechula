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
    
    # URLs de Gestión de Usuarios (CRUD)
    path('usuarios/', views.lista_usuarios, name='lista_usuarios'),
    path('usuarios/crear/', views.crear_usuario, name='crear_usuario'),
    path('usuarios/editar/<int:id_usuario>/', views.editar_usuario, name='editar_usuario'),
    path('usuarios/eliminar/<int:id_usuario>/', views.eliminar_usuario, name='eliminar_usuario'),
    
    # URLs de Propietario
    path('mis-propiedades/', views.mis_propiedades, name='mis_propiedades'),
    path('mis-propiedades/editar/<int:id_punto>/', views.editar_mi_propiedad, name='editar_mi_propiedad'),
    
    # URLs de mapas y geolocalización
    path('mapa/', views.mapa, name='mapa'),
    
    # URLs de respaldo
    path('backup/', views.backup_database, name='backup_database'),
    
    # URLs de gráficas y estadísticas
    path('estadistica/', views.graficos_indicadores, name='estadistica'),
    path('vista_graficas/', views.vista_graficas, name='vista_graficas'),
    
    
    
    path('panel/', views.panel_documentos, name='panel_documentos'),

    path('subir-documento/', views.subir_documento, name='subir_documento'),
    path('editar-documento/<int:id>/', views.editar_documento, name='editar_documento'),
    path('descargar/<int:id>/', views.descargar_documento, name='descargar_documento'),
    path('eliminar/<int:id>/', views.eliminar_documento, name='eliminar_documento'),
    path('api/documentos/<str:categoria_id>/', views.obtener_documentos_categoria, name='documentos_categoria'),
    path('repositorio/', views.repositorio, name='repositorio'),
    path('repositorio-galeria-prueba/', views.repositorio, name='repositorio_galeria_prueba'),
    path('estadistica/', views.graficos_indicadores, name='estadistica'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('dashboard/categoria/<int:category_id>/', views.category_detail_view, name='category_detail'),
    path('api/indicator/<int:indicator_id>/chart-data/', views.indicator_chart_data, name='indicator_chart_data'),
    
    path('registros/', views.registro_visita, name='lista_registros'),  # Cambia 'registro' a 'lista_registros' si es necesario
    path('registros/crear/', views.formulario, name='crear_registro'),  # Nueva URL para crear registro
    path('registros/<int:id_registro>/', views.obtener_registro, name='obtener_registro'),
    path('registros/editar/<int:id_registro>/', views.editar_registro, name='editar_registro'),
    path('registros/eliminar/<int:id_registro>/', views.eliminar_registro, name='eliminar_registro'),
    
    path('registro/', views.formulario, name='registro'),
        
        
  
    path('subir-url/', views.subir_desde_url, name='subir_desde_url'),

    path('archivos/detalle/<int:archivo_id>/', views.detalle_archivo, name='detalle_archivo'),
    path('archivos/editar/<int:archivo_id>/', views.editar_archivo, name='editar_archivo'),
    path('lista-archivos/', views.lista_archivos, name='lista_archivos'),

    path('procesar/<int:archivo_id>/', views.procesar_archivo, name='procesar_archivo'),
    path('actualizar-url/<int:archivo_id>/', views.actualizar_desde_url, name='actualizar_desde_url'),
    path('eliminar/<int:archivo_id>/', views.eliminar_archivo, name='eliminar_archivo'),
    path('crear-categoria/', views.crear_categoria, name='crear_categoria'),
    # Verificación masiva
    path('verificar-urls/', views.verificar_urls, name='verificar_urls'),
    path('archivos/api/categorias/', views.get_categorias_json, name='get_categorias_json'),
    
    
    path('puntos-interes/', views.lista_puntos, name='lista_puntos_interes'),
    path('puntos/detalle/<int:punto_id>/', views.detalle_punto, name='detalle_punto'),
    path('puntos/editar/<int:punto_id>/', views.editar_punto, name='editar_punto'),
    
    path('puntos/toggle-visibilidad/<int:punto_id>/', views.toggle_visibilidad, name='toggle_visibilidad'),

    # =====================================================
    # API RESEÑAS GLOBALES DEL MUNICIPIO
    # =====================================================
    path('api/resenas/', views.api_resenas_globales, name='api_resenas_globales'),
    path('api/resenas/<int:resena_id>/like/', views.like_resena, name='like_resena'),
    path('api/resenas/<int:resena_id>/reportar/', views.reportar_resena, name='reportar_resena'),
    path('api/visitor-stats/', views.api_visitor_stats, name='api_visitor_stats'),

    # Gestión administrativa de reseñas
    path('resenas/', views.gestionar_resenas, name='gestionar_resenas'),
    path('resenas/<int:resena_id>/estado/', views.cambiar_estado_resena, name='cambiar_estado_resena'),
    path('resenas/<int:resena_id>/eliminar/', views.eliminar_resena_admin, name='eliminar_resena_admin'),
    path('resenas/accion-masiva/', views.accion_masiva_resenas, name='accion_masiva_resenas'),

    # =====================================================
    # CHATBOT CON IA
    # ===================================================== 
    path('api/chatbot/', views.chatbot_api, name='chatbot_api'),

    # =====================================================
    # INEGI y Dashboard
    # =====================================================
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('dashboard/categoria/<int:category_id>/', views.category_detail_view, name='category_detail'),
    path('api/indicator/<int:indicator_id>/chart-data/', views.indicator_chart_data, name='indicator_chart_data'),
    path('api/indicator/<int:indicator_id>/jsonstat/', views.indicator_jsonstat_data, name='indicator_jsonstat'),
    path('api/compare-municipalities/', views.compare_municipalities_view, name='compare_municipalities'),

    # =====================================================
    # Portal Encuestador
    # =====================================================
    path('encuestador/', views.encuestador_dashboard, name='encuestador_dashboard'),
    path('encuestador/residente/', views.nueva_encuesta_residente, name='nueva_encuesta_residente'),
    path('encuestador/comercio/', views.nueva_encuesta_comercio, name='nueva_encuesta_comercio'),

    
]

