"""
Script para actualizar el nivel geográfico de los indicadores.
Basado en la disponibilidad real de datos en fuentes oficiales.
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from myapp.models import Indicador

# ── Indicadores a nivel ESTATAL (Puebla = '21') ──────────────────────────────
# Datos disponibles en encuestas del INEGI a nivel estatal (ENOE, ENVIPE, ENVT)
NIVEL_ESTATAL = [
    'Tasa de homicidios',          # SESNSP - solo disponible a nivel estatal
    'Tasa de desocupacion',        # ENOE - trimestral por estado
    'Informalidad laboral',        # ENOE - por estado
    'Tasa de condiciones criticas de ocupacion',  # ENOE
    'Participacion economica',     # ENOE
    'Percepcion de inseguridad',   # ENVIPE - anual por estado
    'Confianza policia',           # ENVIPE
    'Incidencia delictiva',        # SESNSP - por estado
    'Indice de intensidad migratoria',  # CONAPO - estatal
    'Gini del ingreso disponible', # ENIGH - bienal por estado
    'Ingreso equivalente disponible de los hogares',  # ENIGH
    'Contaminacion del aire',      # INECC / SINAICA - estatal
    'Tasa de obesidad',            # ENSANUT - estatal
    'Razon de mortalidad materna', # SSA - estatal
    'Desercion escolar',           # SEP - estatal
    'Niveles de educacion',        # SEP - estatal
]

# ── Indicadores a nivel NACIONAL ('00') ──────────────────────────────────────
NIVEL_NACIONAL = [
    'Acceso a los servicios de banda ancha',  # ENDUTIH - nacional/estatal
    'Disposicion de residuos',     # SEMARNAT - nacional
    'Alternativas de gestion comunitaria de medio ambiente',
    'Vivienda con acceso de servicios basicos',  # Censos - más representativo nacional
    'Habitaciones por persona',
    'Viviendas con techos de materiales resistentes',
]

# ── Indicadores que se quedan MUNICIPALES ────────────────────────────────────
# (Datos censales o de fuente local directa)
# Esperanza de vida al nacer, Tasa de natalidad, Tasa de mortalidad infantil,
# Acceso a servicios de salud, Grado promedio de escolaridad,
# Tasa de alfabetización, Población total, Población en pobreza, etc.
# También todos los de PCI, Turismo y Tradición (son datos locales)

def normalizar(texto):
    """Normaliza texto quitando tildes y pasando a minúsculas."""
    import unicodedata
    texto = unicodedata.normalize('NFD', texto)
    texto = ''.join(c for c in texto if unicodedata.category(c) != 'Mn')
    return texto.lower()

def update_levels():
    updated_estatal = 0
    updated_nacional = 0

    all_indicators = Indicador.objects.all()

    for indicador in all_indicators:
        nombre_norm = normalizar(indicador.nombre)
        matched = False

        for patron in NIVEL_ESTATAL:
            if normalizar(patron) in nombre_norm:
                indicador.nivel_geografico = 'estado'
                indicador.geo_code = '21'  # Puebla
                indicador.save()
                print(f"[ESTATAL]   {indicador.nombre}")
                updated_estatal += 1
                matched = True
                break

        if not matched:
            for patron in NIVEL_NACIONAL:
                if normalizar(patron) in nombre_norm:
                    indicador.nivel_geografico = 'nacional'
                    indicador.geo_code = '00'
                    indicador.save()
                    print(f"[NACIONAL]  {indicador.nombre}")
                    updated_nacional += 1
                    matched = True
                    break

    print(f"\n{'='*60}")
    print(f"Actualizados a ESTATAL:   {updated_estatal}")
    print(f"Actualizados a NACIONAL:  {updated_nacional}")
    sin_cambio = all_indicators.count() - updated_estatal - updated_nacional
    print(f"Sin cambio (MUNICIPAL):   {sin_cambio}")
    print(f"{'='*60}")

if __name__ == '__main__':
    update_levels()
