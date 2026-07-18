import django
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from myapp.models import EncuestaResidente, EncuestaComercio

print(f"Total EncuestaResidente: {EncuestaResidente.objects.count()}")
print(f"Total EncuestaComercio: {EncuestaComercio.objects.count()}")

try:
    from myapp.models import RespuestaEncuesta, Encuesta
    print(f"Total Encuestas Personalizadas: {Encuesta.objects.count()}")
    print(f"Total Respuestas Encuestas Personalizadas: {RespuestaEncuesta.objects.count()}")
except ImportError:
    print("Modelos RespuestaEncuesta o Encuesta no encontrados.")
except Exception as e:
    print(f"Error checking custom surveys: {e}")
