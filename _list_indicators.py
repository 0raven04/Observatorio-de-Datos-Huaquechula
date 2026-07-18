import django
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from myapp.models import Eje, CategoriaIndicador, Indicador

print("Ejes, Categorias e Indicadores Registrados:")
for eje in Eje.objects.all():
    print(f"\n[Eje] {eje.id}: {eje.nombre}")
    for cat in eje.categorias.all():
        print(f"  [Cat] {cat.id}: {cat.nombre}")
        for ind in cat.indicadores.all():
            last_med = ind.mediciones.order_by('-periodo').first()
            val_str = f"{last_med.valor} ({last_med.periodo})" if last_med else "No measurements"
            print(f"    [Ind] {ind.id}: {ind.nombre} | Última medición: {val_str}")
