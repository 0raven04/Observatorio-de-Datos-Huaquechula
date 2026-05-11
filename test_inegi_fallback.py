import os
import django
import requests

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from myapp.services.inegi_service import get_inegi_service

service = get_inegi_service()

KNOWN_IDS = {
    'Esperanza de vida al nacer': '6207019048',
    'Tasa de mortalidad infantil': '6207019049',
    'Acceso a servicios de salud': '6207047047',
    'Tasa de natalidad': '6207019051',
    'Grado promedio de escolaridad': '6207019050',
    'Tasa de alfabetización': '6207019053',
    'Población en pobreza': '6200240364',
    'Población en pobreza extrema': '6200240365',
    'Población total': '1002000001',
    'Tasa de desempleo': '6207047054',
}

GEO_CODES = {
    '21071': 'Municipal (Huaquechula)',
    '21': 'Estatal (Puebla)',
    '00': 'Nacional (México)'
}

print("Prueba de disponibilidad de datos en diferentes niveles geográficos:")

for name, ind_id in KNOWN_IDS.items():
    print(f"\n--- {name} ({ind_id}) ---")
    for geo_code, geo_name in GEO_CODES.items():
        # Override geo code temporarily
        service.HUAQUECHULA_CODE = geo_code
        data = service.fetch_indicator_data(ind_id)
        if data:
            years = list(data.keys())
            years.sort()
            print(f"  ✅ {geo_name}: {len(data)} periodos ({years[0]} - {years[-1]}). Ej: {data[years[-1]]}")
            break # Stop at the most granular level that has data
        else:
            print(f"  ❌ {geo_name}: Sin datos")
