import django
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from myapp.utils_surveys import update_survey_indicators
from myapp.models import Medicion

print("Calculando e inicializando mediciones de encuestas para 2026...")
try:
    update_survey_indicators()
    print("Calculo completado con exito!")
except Exception as e:
    print(f"Error al calcular indicadores: {e}")

print("\nMediciones registradas para el periodo 2026:")
mediciones_2026 = Medicion.objects.filter(periodo="2026")
if mediciones_2026.exists():
    for med in mediciones_2026:
        print(f"   - Indicador ID {med.indicador.id} ({med.indicador.nombre}): {med.valor} (Eje: {med.indicador.categoria.eje.nombre})")
else:
    print("   No se encontraron mediciones para el periodo 2026.")
