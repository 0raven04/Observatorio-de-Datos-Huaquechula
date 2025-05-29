from django.urls import path
from .views import registro_visita
from myapp.views import backup_database
from . import views



urlpatterns = [
    path('backup/', views.backup_database, name='backup_database'),
    path('vista_admin/', views.vista_admin, name='vista_admin'),
    path('registroED/', views.registroED, name='registroED'),
    path('principio/', views.principio, name='principio'),
    path('formulario/editar/', views.editarFormulario, name='editarFormulario'),
    path('formulario/eliminar/<int:id>', views.eliminarFormulario, name='eliminarFormulario'),
]