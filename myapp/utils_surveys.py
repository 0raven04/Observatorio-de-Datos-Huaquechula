from django.utils import timezone
from django.db.models import Avg, Sum, Count
from .models import (
    Indicador, Medicion, EncuestaResidente, 
    EncuestaVisitante, EncuestaInstitucional
)

def update_survey_indicators():
    """
    Calcula los indicadores del Observatorio a partir de las encuestas registradas
    para el año en curso y crea o actualiza las correspondientes mediciones en la BD.
    """
    year_str = str(timezone.now().year)
    
    # ----------------------------------------------------
    # 1. Encuestas de Residentes (Filtro por año)
    # ----------------------------------------------------
    resident_qs = EncuestaResidente.objects.filter(fecha__year=year_str)
    has_residents = resident_qs.exists()
    
    if has_residents:
        # ID 34: Tensión sobre la población local
        t_fest_vals = [r.tension_festividades for r in resident_qs if r.tension_festividades is not None]
        if t_fest_vals:
            val = sum(t_fest_vals) / len(t_fest_vals)
            _update_medicion(34, year_str, val)
            
        # ID 35: Acceso de la población a servicios públicos durante la tradición
        # Excelente (1) -> 100%, Regular (2) -> 50%, Deficiente (3) -> 0%
        acceso_mapping = {1: 100.0, 2: 50.0, 3: 0.0}
        acceso_vals = [acceso_mapping[r.acceso_servicios_festividades] 
                       for r in resident_qs 
                       if r.acceso_servicios_festividades in acceso_mapping]
        if acceso_vals:
            val = sum(acceso_vals) / len(acceso_vals)
            _update_medicion(35, year_str, val)
            
        # ID 36: Tensiones físicas y simbólicas sobre la tradición
        # 1, 2 o 3 en la BD
        perdida_vals = [r.perdida_tradicion for r in resident_qs if r.perdida_tradicion is not None]
        if perdida_vals:
            val = sum(perdida_vals) / len(perdida_vals)
            _update_medicion(36, year_str, val)
            
        # ID 37: Procesos de salvaguardia del Patrimonio (Participación en preservación de Residentes)
        # 1 (Directa) -> 3.0, 2 (Apoyo) -> 2.0, 3 (Ninguna) -> 1.0
        pres_mapping = {1: 3.0, 2: 2.0, 3: 1.0}
        pres_vals = [pres_mapping[r.participacion_preservacion] 
                     for r in resident_qs 
                     if r.participacion_preservacion in pres_mapping]
        if pres_vals:
            val = sum(pres_vals) / len(pres_vals)
            _update_medicion(37, year_str, val)

        # ID 41: Participación de la comunidad en la toma de decisiones
        # regular -> 100%, no_toman_cuenta -> 50%, nunca -> 0%
        dec_mapping = {'regular': 100.0, 'no_toman_cuenta': 50.0, 'nunca': 0.0}
        dec_vals = [dec_mapping[r.participacion_decisiones] 
                    for r in resident_qs 
                    if r.participacion_decisiones in dec_mapping]
        if dec_vals:
            val = sum(dec_vals) / len(dec_vals)
            _update_medicion(41, year_str, val)

        # ID 42: Capacitación, información y comunicación
        # continua -> 5.0, aislada -> 3.0, ninguna -> 1.0
        cap_mapping = {'continua': 5.0, 'aislada': 3.0, 'ninguna': 1.0}
        cap_vals = [cap_mapping[r.capacitacion_turistica] 
                    for r in resident_qs 
                    if r.capacitacion_turistica in cap_mapping]
        if cap_vals:
            val = sum(cap_vals) / len(cap_vals)
            _update_medicion(42, year_str, val)

        # ID 45: Proyectos turísticos (Conteo de residentes con beneficio)
        ben_count = resident_qs.filter(beneficio_economico__in=['principal', 'complementaria']).count()
        _update_medicion(45, year_str, ben_count)

        # ID 40: Relación comunidad - PCI (Interés de jóvenes en tradiciones)
        # activa -> 5.0, parcialmente -> 3.0, perdiendo -> 1.0
        jov_mapping = {'activa': 5.0, 'parcialmente': 3.0, 'perdiendo': 1.0}
        jov_vals = [jov_mapping[r.interes_jovenes] 
                    for r in resident_qs 
                    if r.interes_jovenes in jov_mapping]
        if jov_vals:
            val = sum(jov_vals) / len(jov_vals)
            _update_medicion(40, year_str, val)

    # ----------------------------------------------------
    # 2. Encuestas Institucionales (Filtro por año)
    # ----------------------------------------------------
    inst_qs = EncuestaInstitucional.objects.filter(fecha__year=year_str)
    has_inst = inst_qs.exists()
    
    if has_inst:
        # ID 38: Seguimiento de salvaguardia
        # si -> 5.0, eventual -> 3.0, no -> 1.0
        seg_mapping = {'si': 5.0, 'eventual': 3.0, 'no': 1.0}
        seg_vals = [seg_mapping[i.seguimiento_salvaguardia] 
                    for i in inst_qs 
                    if i.seguimiento_salvaguardia in seg_mapping]
        if seg_vals:
            val = sum(seg_vals) / len(seg_vals)
            _update_medicion(38, year_str, val)

        # ID 39: Difusión de PCI
        # Contar canales de difusión seleccionados
        dif_vals = []
        for i in inst_qs:
            if i.canales_difusion:
                channels = [c.strip() for c in i.canales_difusion.split(',') if c.strip()]
                # Si seleccionaron "Ninguno" o no seleccionaron nada, es 0
                if len(channels) == 1 and channels[0] == 'Ninguno':
                    dif_vals.append(0)
                else:
                    dif_vals.append(len(channels))
            else:
                dif_vals.append(0)
        if dif_vals:
            val = sum(dif_vals) / len(dif_vals)
            _update_medicion(39, year_str, val)

        # ID 43: Regulación
        # reglamento -> 5.0, normas_basicas -> 3.0, no -> 1.0
        reg_mapping = {'reglamento': 5.0, 'normas_basicas': 3.0, 'no': 1.0}
        reg_vals = [reg_mapping[i.regulacion] 
                    for i in inst_qs 
                    if i.regulacion in reg_mapping]
        if reg_vals:
            val = sum(reg_vals) / len(reg_vals)
            _update_medicion(43, year_str, val)

        # ID 44: Herramientas de gestión
        # si -> 5.0, general -> 3.0, no -> 1.0
        gest_mapping = {'si': 5.0, 'general': 3.0, 'no': 1.0}
        gest_vals = [gest_mapping[i.gestion_tecnica] 
                     for i in inst_qs 
                     if i.gestion_tecnica in gest_mapping]
        if gest_vals:
            val = sum(gest_vals) / len(gest_vals)
            _update_medicion(44, year_str, val)

        # ID 46: Integración turística territorial
        # mas_50 -> 5.0, entre_25_50 -> 3.0, menos_25 -> 1.0
        int_mapping = {'mas_50': 5.0, 'entre_25_50': 3.0, 'menos_25': 1.0}
        int_vals = [int_mapping[i.integracion_territorial] 
                    for i in inst_qs 
                    if i.integracion_territorial in int_mapping]
        if int_vals:
            val = sum(int_vals) / len(int_vals)
            _update_medicion(46, year_str, val)

        # ID 4 y ID 56: Visitantes anuales
        anual_vals = [i.visitantes_anual for i in inst_qs if i.visitantes_anual is not None]
        if anual_vals:
            val = sum(anual_vals) / len(anual_vals)
            _update_medicion(4, year_str, val)
            _update_medicion(56, year_str, val)

        # ID 55: Afluencia durante la tradición
        trad_vals = [i.visitantes_festividades for i in inst_qs if i.visitantes_festividades is not None]
        if trad_vals:
            val = sum(trad_vals) / len(trad_vals)
            _update_medicion(55, year_str, val)

    # ----------------------------------------------------
    # 3. Encuestas de Visitantes (Filtro por año)
    # ----------------------------------------------------
    visitor_qs = EncuestaVisitante.objects.filter(fecha__year=year_str)
    has_visitor = visitor_qs.exists()
    
    if has_visitor:
        # ID 57: Índice de satisfacción (promedio 1-5)
        sat_vals = [v.satisfaccion for v in visitor_qs if v.satisfaccion is not None]
        if sat_vals:
            val = sum(sat_vals) / len(sat_vals)
            _update_medicion(57, year_str, val)


def _update_medicion(indicator_id, period, value):
    """
    Función auxiliar para crear o actualizar la medición de un indicador.
    """
    try:
        indicador = Indicador.objects.get(id=indicator_id)
        medicion, created = Medicion.objects.update_or_create(
            indicador=indicador,
            periodo=period,
            defaults={'valor': round(value, 2)}
        )
        status = "creada" if created else "actualizada"
        print(f"Medición {status} para Indicador ID {indicator_id} ({period}): {value}")
    except Indicador.DoesNotExist:
        print(f"Error: No se encontró el indicador con ID {indicator_id}")
    except Exception as e:
        print(f"Error al actualizar medición para Indicador {indicator_id}: {e}")
