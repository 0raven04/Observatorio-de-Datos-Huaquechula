"""
Aplica los IDs de INEGI confirmados a los indicadores de Bienestar Social.
Solo actualiza los que respondieron exitosamente a la API.
"""
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from myapp.models import Indicador

# IDs confirmados que responden correctamente a la API del INEGI
CONFIRMED = [
    # (nombre_busqueda, inegi_id, geo_code, nivel_geografico)
    ("Razón de mortalidad materna",        "6207019042", "21",    "estado"),
    ("Tasa de mortalidad",                 "6207019049", "21071", "municipal"),
    ("Gini del ingreso disponible",        "6200240320", "21",    "estado"),
    ("Índice de intensidad migratoria",    "6200240316", "21",    "estado"),
]

print("Actualizando indicadores con IDs de INEGI confirmados...\n")

for nombre_busq, inegi_id, geo_code, nivel in CONFIRMED:
    inds = Indicador.objects.filter(nombre__icontains=nombre_busq)
    if not inds.exists():
        print(f"  [NO ENCONTRADO] '{nombre_busq}'")
        continue
    for ind in inds:
        ind.inegi_indicator_id = inegi_id
        ind.data_source = 'inegi'
        ind.geo_code = geo_code
        ind.nivel_geografico = nivel
        ind.save()
        print(f"  [OK] '{ind.nombre}' → ID: {inegi_id} | geo: {geo_code} | nivel: {nivel}")

print("\nProceso completado.")
