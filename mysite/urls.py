"""
URL configuration for mysite project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/

Este es el archivo principal de configuración de URLs del proyecto Django.
Define las rutas URL globales y cómo se mapean a las vistas.
"""

from django.contrib import admin
from django.urls import path, include
from myapp import views as myapp_views
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LogoutView
from django.shortcuts import redirect
from myapp import views
from myapp.views import backup_database
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

urlpatterns = [
    # Inicio de sesión
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),

    # Cierre de sesión
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),

    # ─── Recuperación de contraseña ──────────────────────────────────────────
    # Paso 1 – El usuario ingresa su correo electrónico
    path(
        'password-reset/',
        views.CustomPasswordResetView.as_view(),
        name='password_reset',
    ),
    # Paso 2 – Confirmación: "revisa tu correo"
    path(
        'password-reset/done/',
        auth_views.PasswordResetDoneView.as_view(
            template_name='registration/password_reset_done.html'
        ),
        name='password_reset_done',
    ),
    # Paso 3 – El usuario hace clic en el enlace del correo → ingresa nueva contraseña
    path(
        'password-reset/confirm/<uidb64>/<token>/',
        views.CustomPasswordResetConfirmView.as_view(),
        name='password_reset_confirm',
    ),
    # Paso 4 – Contraseña cambiada exitosamente
    path(
        'password-reset/complete/',
        auth_views.PasswordResetCompleteView.as_view(
            template_name='registration/password_reset_complete.html'
        ),
        name='password_reset_complete',
    ),
    
    # URL para cerrar sesión (versión 2 - redundante)
    # - Esta es una definición duplicada que debería eliminarse
    # path('logout/', LogoutView.as_view(next_page='login'),  name='logout'),
    
    # URL para generar respaldo de la base de datos
    # - Llama a la vista backup_database definida en myapp/views.py
    # - Nombre de la ruta: 'backup_database'
    path('backup/', backup_database, name='backup_database'),

    # URL para acceder a la vista de gráficos e indicadores turísticos
    path('graficos_indicadores/', views.graficos_indicadores, name='graficos_indicadores'),
    # URL raíz que incluye las URLs de la aplicación 'myapp'
    path('', include('myapp.urls')),

    # API REST para la app móvil (JWT, CRUD visitas, indicadores)
    path('', include('myapp.api_urls')),

    # API Pública Open Data (/api/v1/public/)
    path('', include('myapp.public_api_urls')),

    # ── Documentación OpenAPI / Swagger ──────────────────────────────────────
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


"""
urlpatterns = [
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('backup/', backup_database, name='backup_database'),
    path('', include('myapp.urls')),
]
"""