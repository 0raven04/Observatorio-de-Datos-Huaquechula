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

urlpatterns = [
    # URL para la página de inicio de sesión
    # - Utiliza la vista de inicio de sesión incorporada de Django
    # - Especifica la plantilla personalizada: registration/login.html
    # - Nombre de la ruta: 'login'
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    
    # NOTA: Hay dos definiciones para 'logout/' - esto es redundante y puede causar confusión
    # Se recomienda mantener solo una definición
    
    # URL para cerrar sesión (versión 1)
    # - Utiliza la vista de cierre de sesión incorporada de Django
    # - Redirige a la página de login después de cerrar sesión
    # - Nombre de la ruta: 'logout'
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    
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
    # - Todas las URLs definidas en myapp.urls estarán bajo la raíz del proyecto
    # - Ejemplo: la ruta 'visitas/' de myapp será accesible como '/visitas/'
    path('', include('myapp.urls')),
]

# Recomendaciones importantes:
# 1. Eliminar la definición duplicada de 'logout/' (línea 30)
# 2. El orden de las URLs es importante - Django procesa los patrones en orden
# 3. Las URLs más específicas deberían definirse primero
# 4. La inclusión de 'myapp.urls' con path('', ...) hace que las URLs de la app sean accesibles desde la raíz

# Estructura final recomendada sin la redundancia:
"""
urlpatterns = [
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('backup/', backup_database, name='backup_database'),
    path('', include('myapp.urls')),
]
"""