from django.urls import path
from .views import registro_visita
from myapp.views import backup_database
from . import views




urlpatterns = [
    path('backup/', views.backup_database, name='backup_database'),
    path('visitas/', views.registro_visita, name='lista_registros'),
    path('visitas/eliminar/<int:id_registro>/', views.eliminar_registro, name='eliminar_registro'),

]