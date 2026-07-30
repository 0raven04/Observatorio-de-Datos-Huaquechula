"""
URLs de la API Móvil del Observatorio.
Prefijo base: /api/mobile/  (configurado en mysite/urls.py)
"""
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .api_views import (
    LoginMobileView,
    PerfilView,
    VisitasListCreateView,
    VisitaDetailView,
    IndicadoresView,
    DashboardSummaryView,
    EncuestaVisitanteView,
    EncuestaResidenteView,
    EncuestaInstitucionalView,
    EncuestaComercioView,
    MisEncuestasView,
    EncuestaCreadaListView,
    ResponderEncuestaView,
)

urlpatterns = [
    # ── Autenticación JWT ─────────────────────────────────────────────────────
    path('api/mobile/login/', LoginMobileView.as_view(), name='api_mobile_login'),
    path('api/mobile/token/refresh/', TokenRefreshView.as_view(), name='api_mobile_token_refresh'),

    # ── Perfil del usuario ────────────────────────────────────────────────────
    path('api/mobile/perfil/', PerfilView.as_view(), name='api_mobile_perfil'),

    # ── Registros de visita ───────────────────────────────────────────────────
    path('api/mobile/visitas/', VisitasListCreateView.as_view(), name='api_mobile_visitas'),
    path('api/mobile/visitas/<int:pk>/', VisitaDetailView.as_view(), name='api_mobile_visita_detail'),

    # ── Indicadores y dashboard ───────────────────────────────────────────────
    path('api/mobile/indicadores/', IndicadoresView.as_view(), name='api_mobile_indicadores'),
    path('api/mobile/dashboard/', DashboardSummaryView.as_view(), name='api_mobile_dashboard'),

    # ── Encuestas (datos manuales del Observatorio) ──────────────────────────
    path('api/mobile/mis-encuestas/', MisEncuestasView.as_view(), name='api_mobile_mis_encuestas'),
    path('api/mobile/encuestas/visitante/', EncuestaVisitanteView.as_view(), name='api_mobile_encuesta_visitante'),
    path('api/mobile/encuestas/residente/', EncuestaResidenteView.as_view(), name='api_mobile_encuesta_residente'),
    path('api/mobile/encuestas/institucional/', EncuestaInstitucionalView.as_view(), name='api_mobile_encuesta_institucional'),
    path('api/mobile/encuestas/comercio/', EncuestaComercioView.as_view(), name='api_mobile_encuesta_comercio'),

    # ── Encuestas Creadas / Dinámicas para Móvil ──────────────────────────────
    path('api/mobile/encuestas-creadas/', EncuestaCreadaListView.as_view(), name='api_mobile_encuestas_creadas'),
    path('api/mobile/encuestas-creadas/<int:pk>/responder/', ResponderEncuestaView.as_view(), name='api_mobile_encuestas_creadas_responder'),
]
