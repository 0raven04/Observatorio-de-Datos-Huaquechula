import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from myapp.models import Indicador

print("=== Sincronizando data_source y encuesta_tipo para indicadores de Encuesta ===")

# Mapeo de indicadores específicos por nombre a su tipo de encuesta
mapping = {
    # Tradición y Patrimonio
    'Talleres de artesanía': 'residente',
    'Tensión sobre la población local': 'residente',
    'Acceso de la población a los servicios públicos durante la tradición': 'residente',
    'Tensiones físicas y simbólicas sobre la tradición': 'residente',
    'Procesos de salvaguardia del Patrimonio': 'institucional',
    'Seguimiento de salvaguardia': 'institucional',
    'Difusión de PCI': 'institucional',
    'Relación comunidad - PCI': 'institucional',
    
    # Turismo Comunitario
    'Visitantes anuales': 'institucional',
    'Participación de la comunidad en la toma de decisiones': 'residente',
    'Capacitación, información y comunicación': 'residente',
    'Regulación': 'institucional',
    'Herramientas de gestión': 'institucional',
    'Proyectos turísticos': 'residente',
    'Integración turística territorial': 'residente',
    
    # Indicadores del evento (Landing)
    'Afluencia durante la tradicion': 'institucional',
    'Indice de satisfaccion': 'visitante',
    'Afluencia por zonas': 'visitante',
    'Visitas por ciudad': 'visitante',
    'Perfil del visitante': 'visitante',
    'Grupo de visita': 'visitante',
    'Actividades populares': 'visitante',
    'Resenas': 'visitante',
}

# Obtener todos los indicadores de los 3 ejes especificados
ejes_nombres = ['Tradición y Patrimonio', 'Turismo Comunitario', 'Indicadores del evento']
inds = Indicador.objects.filter(categoria__eje__nombre__in=ejes_nombres)

updated_count = 0
for ind in inds:
    # 1. Asegurar que data_source sea 'encuesta'
    ind.data_source = 'encuesta'
    
    # 2. Asignar el encuesta_tipo correspondiente basado en el mapeo
    tipo = mapping.get(ind.nombre)
    if tipo:
        ind.encuesta_tipo = tipo
        ind.save()
        print(f"- Actualizado: '{ind.nombre}' -> data_source='encuesta', encuesta_tipo='{tipo}'")
        updated_count += 1
    else:
        # Fallback si no está mapeado exactamente
        if 'anual' in ind.nombre.lower() or 'afluencia' in ind.nombre.lower():
            ind.encuesta_tipo = 'institucional'
        else:
            ind.encuesta_tipo = 'residente'
        ind.save()
        print(f"- Fallback: '{ind.nombre}' -> data_source='encuesta', encuesta_tipo='{ind.encuesta_tipo}'")
        updated_count += 1

print(f"\n=== Sincronización completada. Total actualizados: {updated_count} ===")
