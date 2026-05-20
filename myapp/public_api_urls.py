"""
URLs de la API Pública Open Data del Observatorio de Datos Huaquechula.
Prefijo base: /api/v1/public/

Grupos:
    1 — Indicadores Territoriales
    2 — Turismo y Visitantes (datos agregados y anonimizados)
    3 — Territorio y Puntos de Interés (GeoJSON)
    4 — Reseñas y Satisfacción
    5 — Encuestas Agregadas
"""
from django.urls import path
from .public_api_views import (
    # Grupo 1 — Indicadores
    EjesPublicView,
    EjeDetailPublicView,
    CategoriasPublicView,
    CategoriaDetailPublicView,
    IndicadoresPublicView,
    IndicadorDetailPublicView,
    IndicadorSerieView,
    IndicadorUltimaView,
    IndicadorJSONStatView,
    # Grupo 2 — Turismo
    TurismoResumenView,
    TurismoVisitantesPorMesView,
    TurismoProcedenciasView,
    TurismoPerfilDemograficoView,
    TurismoMotivosView,
    TurismoTransporteView,
    TurismoEstanciaView,
    # Grupo 3 — Territorio
    PuntosInteresPublicView,
    PuntoInteresDetailPublicView,
    SitiosTuristicosPublicView,
    RutasPublicView,
    OfrendasPublicView,
    # Grupo 4 — Reseñas
    ResenasPublicView,
    ResenasEstadisticasView,
    # Grupo 5 — Encuestas agregadas
    EncuestaResidenteResumenView,
    EncuestaComercioResumenView,
)

urlpatterns = [
    # ── GRUPO 1: Indicadores Territoriales ───────────────────────────────────
    path('api/v1/public/ejes/', EjesPublicView.as_view(), name='public_ejes'),
    path('api/v1/public/ejes/<int:pk>/', EjeDetailPublicView.as_view(), name='public_eje_detail'),
    path('api/v1/public/categorias/', CategoriasPublicView.as_view(), name='public_categorias'),
    path('api/v1/public/categorias/<int:pk>/', CategoriaDetailPublicView.as_view(), name='public_categoria_detail'),
    path('api/v1/public/indicadores/', IndicadoresPublicView.as_view(), name='public_indicadores'),
    path('api/v1/public/indicadores/<int:pk>/', IndicadorDetailPublicView.as_view(), name='public_indicador_detail'),
    path('api/v1/public/indicadores/<int:pk>/serie/', IndicadorSerieView.as_view(), name='public_indicador_serie'),
    path('api/v1/public/indicadores/<int:pk>/ultima/', IndicadorUltimaView.as_view(), name='public_indicador_ultima'),
    path('api/v1/public/indicadores/<int:pk>/jsonstat/', IndicadorJSONStatView.as_view(), name='public_indicador_jsonstat'),

    # ── GRUPO 2: Turismo y Visitantes ─────────────────────────────────────────
    path('api/v1/public/turismo/resumen/', TurismoResumenView.as_view(), name='public_turismo_resumen'),
    path('api/v1/public/turismo/visitantes-por-mes/', TurismoVisitantesPorMesView.as_view(), name='public_turismo_por_mes'),
    path('api/v1/public/turismo/procedencias/', TurismoProcedenciasView.as_view(), name='public_turismo_procedencias'),
    path('api/v1/public/turismo/perfil-demografico/', TurismoPerfilDemograficoView.as_view(), name='public_turismo_demografico'),
    path('api/v1/public/turismo/motivos/', TurismoMotivosView.as_view(), name='public_turismo_motivos'),
    path('api/v1/public/turismo/transporte/', TurismoTransporteView.as_view(), name='public_turismo_transporte'),
    path('api/v1/public/turismo/estancia/', TurismoEstanciaView.as_view(), name='public_turismo_estancia'),

    # ── GRUPO 3: Territorio y Puntos de Interés ───────────────────────────────
    path('api/v1/public/puntos-interes/', PuntosInteresPublicView.as_view(), name='public_puntos_interes'),
    path('api/v1/public/puntos-interes/<int:pk>/', PuntoInteresDetailPublicView.as_view(), name='public_punto_interes_detail'),
    path('api/v1/public/sitios-turisticos/', SitiosTuristicosPublicView.as_view(), name='public_sitios_turisticos'),
    path('api/v1/public/rutas/', RutasPublicView.as_view(), name='public_rutas'),
    path('api/v1/public/ofrendas/', OfrendasPublicView.as_view(), name='public_ofrendas'),

    # ── GRUPO 4: Reseñas y Satisfacción ──────────────────────────────────────
    path('api/v1/public/resenas/', ResenasPublicView.as_view(), name='public_resenas'),
    path('api/v1/public/resenas/estadisticas/', ResenasEstadisticasView.as_view(), name='public_resenas_estadisticas'),

    # ── GRUPO 5: Encuestas Agregadas ──────────────────────────────────────────
    path('api/v1/public/encuestas/residente/resumen/', EncuestaResidenteResumenView.as_view(), name='public_encuesta_residente'),
    path('api/v1/public/encuestas/comercio/resumen/', EncuestaComercioResumenView.as_view(), name='public_encuesta_comercio'),
]
