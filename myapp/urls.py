from django.urls import path
from .views import registro_visita

urlpatterns = [
    path('', registro_visita, name='registro'),
]