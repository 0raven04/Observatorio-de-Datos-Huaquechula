from django.urls import path
from .views import registro_visita
from myapp.views import backup_database
from . import views



urlpatterns = [
    path('', registro_visita, name='registro'),
    path('backup/', views.backup_database, name='backup_database'),
]