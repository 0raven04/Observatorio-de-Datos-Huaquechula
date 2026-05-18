"""
Prueba de IDs de INEGI para indicadores de Bienestar Social sin mapeo.
Verifica cuales responden correctamente y cuales no.
"""
import os, django, requests
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.conf import settings

TOKEN = getattr(settings, 'INEGI_API_TOKEN', '')
BASE = "https://www.inegi.org.mx/app/api/indicadores/desarrolladores/jsonxml/INDICATOR"
VERSION = "2.0"

# Candidatos a testear: {nombre_indicador: (id, geo_code, nivel)}
# IDs basados en el catálogo oficial del Banco de Indicadores INEGI
CANDIDATES = {
    # SALUD
    "Razón de mortalidad materna": ("6207019042", "21", "estado"),
    "Tasa de mortalidad": ("6207019049", "21071", "municipal"),

    # ACCESIBILIDAD A SERVICIOS
    "Vivienda con acceso a servicios básicos - agua": ("6207047048", "21071", "municipal"),
    "Vivienda con acceso a servicios básicos - drenaje": ("6207047050", "21071", "municipal"),
    "Vivienda con acceso a servicios básicos - electricidad": ("6207047049", "21071", "municipal"),
    "Acceso a servicios de banda ancha (hogares)": ("6200240295", "00", "nacional"),
    "Viviendas con internet": ("6200240296", "00", "nacional"),

    # VIVIENDA
    "Habitaciones por persona": ("6207047052", "21071", "municipal"),
    "Viviendas con techos resistentes": ("6207047051", "21071", "municipal"),

    # EDUCACION
    "Deserción escolar primaria": ("6200240270", "21", "estado"),
    "Niveles de educación (población sin escolaridad)": ("6200240240", "21071", "municipal"),

    # INGRESOS
    "Gini coeficiente": ("6200240320", "21", "estado"),

    # EMPLEO (ENOE)
    "Tasa de desocupación": ("444559", "21", "estado"),
    "Informalidad laboral": ("444579", "21", "estado"),
    "Tasa de condiciones críticas de ocupación": ("444581", "21", "estado"),
    "Participación económica (PEA)": ("444553", "21", "estado"),

    # SEGURIDAD (SESNSP via INEGI)
    "Incidencia delictiva": ("6200240394", "21", "estado"),
    "Tasa de homicidios": ("6200240383", "21", "estado"),

    # MIGRACIÓN
    "Índice de intensidad migratoria": ("6200240316", "21", "estado"),
}

print(f"Token activo: {'Sí' if TOKEN else 'NO (falta configurar)'}\n")
print(f"{'INDICADOR':<55} {'ID':<15} {'GEO':<8} {'NIVEL':<10} {'RESULTADO'}")
print("=" * 110)

ok = []
fail = []

for nombre, (ind_id, geo, nivel) in CANDIDATES.items():
    url = f"{BASE}/{ind_id}/es/{geo}/false/BISE/{VERSION}/{TOKEN}?type=json"
    try:
        r = requests.get(url, timeout=15)
        if r.status_code == 200:
            data = r.json()
            obs = data.get('Series', [{}])[0].get('OBSERVATIONS', [])
            resultado = f"OK ({len(obs)} periodos)"
            ok.append((nombre, ind_id, geo, nivel))
        else:
            resultado = f"HTTP {r.status_code}"
            fail.append((nombre, ind_id, geo, nivel, f"HTTP {r.status_code}"))
    except Exception as e:
        resultado = f"Error: {e}"
        fail.append((nombre, ind_id, geo, nivel, str(e)))
    
    print(f"{nombre:<55} {ind_id:<15} {geo:<8} {nivel:<10} {resultado}")

print(f"\n{'='*110}")
print(f"Exitosos: {len(ok)}")
print(f"Fallidos: {len(fail)}")

if fail:
    print("\nIndicadores que NO responden:")
    for item in fail:
        print(f"  - {item[0]} (ID: {item[1]}, geo: {item[2]}) → {item[4]}")
