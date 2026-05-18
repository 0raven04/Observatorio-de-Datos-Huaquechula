import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from myapp.models import Eje, Indicador

eje = Eje.objects.filter(nombre__icontains='Bienestar').first()
if not eje:
    print("No se encontró eje de Bienestar Social")
else:
    print(f"Eje: {eje.nombre}\n")
    for cat in eje.categorias.all():
        print(f"  Categoría: {cat.nombre}")
        for ind in cat.indicadores.all():
            print(f"    - {ind.nombre} | fuente: {ind.data_source} | nivel: {ind.nivel_geografico} | inegi_id: {ind.inegi_indicator_id}")
