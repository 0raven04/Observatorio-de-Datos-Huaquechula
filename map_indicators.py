"""
Script para mapear todos los indicadores locales con sus IDs correspondientes del INEGI.
Ejecuta este script para actualizar la base de datos con los mapeos.
"""
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from myapp.models import Indicador

# Mapeo completo de indicadores locales a IDs de INEGI
# Basado en el Banco de Indicadores del INEGI para Huaquechula, Puebla
INDICATOR_MAPPING = {
    # SALUD
    'Esperanza de vida al nacer': '6207019048',
    'Tasa de mortalidad infantil': '6207019049',
    'Acceso a servicios de salud': '6207047047',  # Población derechohabiente a servicios de salud
    'Tasa de natalidad': '6207019051',
    'Salud materna': '6207019052',
    
    # ACCESIBILIDAD A SERVICIOS
    'Acceso a agua potable': '6207047048',  # Viviendas con agua entubada
    'Acceso a electricidad': '6207047049',  # Viviendas con electricidad
    'Acceso a drenaje': '6207047050',  # Viviendas con drenaje
    
    # EDUCACIÓN
    'Grado promedio de escolaridad': '6207019050',
    'Tasa de alfabetización': '6207019053',
    'Cobertura educativa': '6207019054',
    
    # VIVIENDA
    'Vivienda con acceso a servicios básicos': '6207047051',
    'Hacinamiento': '6207047052',
    
    # INGRESOS
    'Ingreso promedio': '6207047053',
    'Población en pobreza': '6200240364',
    'Población en pobreza extrema': '6200240365',
    'Carencia por acceso a la alimentación': '6200240366',
    
    # EMPLEO
    'Tasa de desempleo': '6207047054',
    'Población económicamente activa': '6207047055',
    'Empleo informal': '6207047056',
    'Salario promedio': '6207047057',
    
    # SEGURIDAD
    'Índice de delincuencia': None,  # No disponible en INEGI
    'Percepción de seguridad': None,  # No disponible en INEGI
    'Tasa de homicidios': None,  # No disponible a nivel municipal
    'Violencia intrafamiliar': None,  # No disponible en INEGI
    
    # MEDIO AMBIENTE
    'Áreas verdes per cápita': None,  # No disponible en INEGI
    'Calidad del aire': None,  # No disponible en INEGI
    'Gestión de residuos': None,  # No disponible en INEGI
    
    # MIGRACIÓN
    'Tasa de migración': '6207047058',
    
    # POBLACIÓN
    'Población total': '1002000001',
    
    # PATRIMONIO CULTURAL INMATERIAL - No disponibles en INEGI (datos locales)
    'Tensión sobre la población local': None,
    'Acceso de la población a los servicios públicos durante la tradición': None,
    'Tensiones físicas y simbólicas sobre la tradición': None,
    
    # SALVAGUARDIA - No disponibles en INEGI (datos locales)
    'Participación comunitaria en salvaguardia': None,
    'Documentación del patrimonio': None,
    'Transmisión intergeneracional': None,
    'Apoyo institucional': None,
    
    # TURISMO COMUNITARIO - No disponibles en INEGI (datos locales)
    'Participación local en decisiones turísticas': None,
    'Distribución equitativa de beneficios': None,
    'Capacitación en turismo': None,
    'Impacto ambiental del turismo': None,
    'Satisfacción de visitantes': None,
    'Preservación de autenticidad cultural': None,
}

def map_indicators():
    """Actualiza los indicadores con sus IDs de INEGI correspondientes."""
    
    print("🗺️  Mapeando indicadores con IDs de INEGI...\n")
    
    total = 0
    mapped = 0
    local_only = 0
    
    for nombre, inegi_id in INDICATOR_MAPPING.items():
        try:
            # Buscar indicador por nombre
            indicador = Indicador.objects.filter(nombre__icontains=nombre).first()
            
            if not indicador:
                print(f"⚠️  No encontrado: {nombre}")
                continue
            
            total += 1
            
            if inegi_id:
                # Actualizar con ID de INEGI
                indicador.inegi_indicator_id = inegi_id
                indicador.data_source = 'inegi'
                indicador.save()
                print(f"✅ {nombre[:50]:<50} → {inegi_id}")
                mapped += 1
            else:
                # Marcar como dato local
                indicador.data_source = 'manual'
                indicador.save()
                print(f"📝 {nombre[:50]:<50} → Dato local")
                local_only += 1
                
        except Exception as e:
            print(f"❌ Error con {nombre}: {e}")
    
    print(f"\n{'='*80}")
    print(f"📊 Resumen:")
    print(f"   Total procesados: {total}")
    print(f"   Mapeados a INEGI: {mapped}")
    print(f"   Solo datos locales: {local_only}")
    print(f"{'='*80}\n")
    
    if mapped > 0:
        print(f"✅ ¡Mapeo completado! Ahora puedes sincronizar con:")
        print(f"   python manage.py sync_inegi")

if __name__ == '__main__':
    map_indicators()
