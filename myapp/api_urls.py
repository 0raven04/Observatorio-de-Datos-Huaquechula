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
    EncuestaResidenteView,
    EncuestaComercioView,
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
    path('api/mobile/encuestas/residente/', EncuestaResidenteView.as_view(), name='api_mobile_encuesta_residente'),
    path('api/mobile/encuestas/comercio/', EncuestaComercioView.as_view(), name='api_mobile_encuesta_comercio'),
]
