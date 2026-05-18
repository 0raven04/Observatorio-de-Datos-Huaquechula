import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from myapp.models import Indicador

print('Lista de indicadores:')
for ind in Indicador.objects.all():
    source = ind.data_source
    level = getattr(ind, 'nivel_geografico', 'municipal')
    print(f'- {ind.nombre} | Fuente: {source} | Origen: {level}')
