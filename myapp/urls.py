from django.urls import path
from .views import registro_visita
from myapp.views import backup_database


urlpatterns = [
    path('', registro_visita, name='registro'),
    path('backup/', backup_database, name='backup_database'),
]