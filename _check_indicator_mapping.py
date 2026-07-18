import django
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from myapp.models import Indicador

print("Indicadores con metadata de encuesta:")
for ind in Indicador.objects.exclude(encuesta_tipo__isnull=True).exclude(encuesta_tipo=""):
    print(f"ID: {ind.id} | Nombre: {ind.nombre} | Tipo: {ind.encuesta_tipo} | Pregunta: {ind.encuesta_pregunta}")
