"""
URL configuration for mysite project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from myapp import views as myapp_views  # 
from django.contrib.auth import views as auth_views
from django.shortcuts import redirect

from django.contrib.auth.views import LogoutView
from myapp import views

from django.contrib import admin
from django.urls import path, include

from myapp.views import backup_database
from django.contrib.auth.views import LogoutView


urlpatterns = [
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('registro/', myapp_views.registro_visita, name='registro'),
     path('logout/', LogoutView.as_view(next_page='login'),  name='logout'),
     path('principal/', views.vista_inicio, name='vista_inicio'),
    path('backup/',backup_database, name='backup_database'),
    path('', include('myapp.urls')),

]