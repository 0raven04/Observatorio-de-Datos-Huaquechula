"""
views_monitoring.py — Endpoints de auditoría, observabilidad y alertas del flujo de datos.
Permite verificar en tiempo real que las encuestas móviles lleguen a PostgreSQL y se reflejen en la web.
"""
import os
import time
import json
import logging
import requests
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from django.utils import timezone
from django.db import connection
from django.db.models import Avg, Max, Count
from django.views.decorators.http import require_GET, require_POST
from django.views.decorators.csrf import csrf_exempt

from .models import (
    EncuestaVisitante, EncuestaResidente, EncuestaInstitucional,
    EncuestaComercio, RegistroVisita, Medicion, Indicador,
    RegistroIngestaEncuesta
)

logger = logging.getLogger(__name__)

def send_whatsapp_alert(mensaje: str) -> dict:
    """
    Envía una alerta a través de un webhook de WhatsApp.
    Soporta webhooks directos (Make, Zapier, CallMeBot, Twilio o puente personalizado).
    La URL se configura en la variable de entorno WHATSAPP_WEBHOOK_URL.
    """
    webhook_url = os.environ.get('WHATSAPP_WEBHOOK_URL', '').strip()
    if not webhook_url:
        logger.info("WHATSAPP_ALERT: Webhook no configurado (WHATSAPP_WEBHOOK_URL vacía). Alerta: %s", mensaje)
        return {"status": "skipped", "message": "WHATSAPP_WEBHOOK_URL no está configurada"}

    try:
        payload = {
            "source": "Observatorio Huaquechula",
            "event": "PIPELINE_ALERT",
            "message": mensaje,
            "timestamp": timezone.now().isoformat()
        }
        res = requests.post(webhook_url, json=payload, timeout=5)
        logger.info("WHATSAPP_ALERT enviada con éxito. Status: %s", res.status_code)
        return {"status": "sent", "http_status": res.status_code}
    except Exception as e:
        logger.error("Error al enviar alerta a WhatsApp webhook: %s", e)
        return {"status": "error", "error": str(e)}


@require_GET
def api_health(request):
    """
    Sonda ligera de salud para Fly.io, Uptime Kuma o Better Stack.
    Retorna 200 OK si la base de datos PostgreSQL responde correctamente.
    """
    t0 = time.time()
    db_ok = True
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
    except Exception as e:
        db_ok = False
        logger.error("Health check fallo en conexion a BD: %s", e)

    latency_ms = round((time.time() - t0) * 1000, 2)
    status_code = 200 if db_ok else 503

    return JsonResponse({
        "status": "healthy" if db_ok else "unhealthy",
        "database": "connected" if db_ok else "disconnected",
        "latency_ms": latency_ms,
        "timestamp": timezone.now().isoformat(),
        "service": "Observatorio Huaquechula Core API"
    }, status=status_code)


@require_GET
def api_survey_flow_status(request):
    """
    Auditoría profunda del flujo de datos en tiempo real:
    - Conteos de cada tipo de encuesta en PostgreSQL.
    - Metadatos de la última encuesta recibida (tipo, ID, minutos transcurridos).
    - Reconciliación: Comprueba que los indicadores estadísticos estén calculados.
    - Detección de posibles cuellos de botella o detención del flujo.
    """
    t0 = time.time()
    current_year = str(timezone.now().year)

    # 1. Conteo de registros en la base de datos
    total_visitantes = EncuestaVisitante.objects.count()
    total_residentes = EncuestaResidente.objects.count()
    total_institucionales = EncuestaInstitucional.objects.count()
    total_comercios = EncuestaComercio.objects.count()
    total_visitas = RegistroVisita.objects.count()
    total_encuestas = total_visitantes + total_residentes + total_institucionales + total_comercios

    # 2. Localizar la encuesta más reciente
    latest_events = []
    last_v = EncuestaVisitante.objects.order_by('-fecha').first()
    if last_v and last_v.fecha:
        latest_events.append(("Visitante", last_v.fecha, last_v.id))
    
    last_r = EncuestaResidente.objects.order_by('-fecha').first()
    if last_r and last_r.fecha:
        latest_events.append(("Residente", last_r.fecha, last_r.id))
        
    last_i = EncuestaInstitucional.objects.order_by('-fecha').first()
    if last_i and last_i.fecha:
        latest_events.append(("Institucional", last_i.fecha, last_i.id))

    latest_events.sort(key=lambda x: x[1], reverse=True)
    latest_info = None
    if latest_events:
        tipo, fecha, eid = latest_events[0]
        mins_ago = round((timezone.now() - fecha).total_seconds() / 60, 1)
        latest_info = {
            "type": tipo,
            "id": eid,
            "timestamp": fecha.isoformat(),
            "minutes_ago": mins_ago
        }

    # 3. Reconciliación con la tabla Medicion (Indicadores)
    # ID 57: Satisfacción promedio del visitante
    # ID 34: Tensión sobre población local
    med_57 = Medicion.objects.filter(indicador_id=57, periodo=current_year).first()
    med_34 = Medicion.objects.filter(indicador_id=34, periodo=current_year).first()

    pipeline_status = "healthy"
    sync_warnings = []

    if total_visitantes > 0 and not med_57:
        pipeline_status = "warning"
        sync_warnings.append("Hay encuestas de visitante pero no se calculó la medición de satisfacción (ID 57).")

    if total_residentes > 0 and not med_34:
        pipeline_status = "warning"
        sync_warnings.append("Hay encuestas de residente pero no se calculó la medición de tensión comunitaria (ID 34).")

    elapsed_ms = round((time.time() - t0) * 1000, 2)

    return JsonResponse({
        "pipeline_status": pipeline_status,
        "database_latency_ms": elapsed_ms,
        "summary": {
            "total_encuestas": total_encuestas,
            "visitantes": total_visitantes,
            "residentes": total_residentes,
            "institucionales": total_institucionales,
            "comercios": total_comercios,
            "registros_visita": total_visitas,
        },
        "latest_survey": latest_info,
        "sync_warnings": sync_warnings,
        "server_time": timezone.now().isoformat()
    })


@csrf_exempt
@require_POST
def test_whatsapp_alert(request):
    """
    Endpoint para probar manualmente el webhook de WhatsApp configurado.
    POST /api/monitoring/test-alert/
    """
    msg = request.POST.get('message') or "Prueba de alerta desde el Observatorio de Datos Huaquechula."
    result = send_whatsapp_alert(f"🧪 [PRUEBA] {msg}")
    return JsonResponse(result)


def monitoreo_en_vivo_view(request):
    """
    Vista web del Centro de Mando Gráfico en Vivo (Mission Control).
    URL: /monitoreo/en-vivo/
    Permite supervisar en tiempo real la ingesta de encuestas en Huaquechula,
    con gráficos de resiliencia de red, lag por cobertura y feed de telemetría.
    """
    return render(request, 'myapp/monitoreo_en_vivo.html')


@require_GET
def api_monitoring_live_stream(request):
    """
    API JSON que alimenta el panel gráfico en tiempo real:
    - Métricas de resiliencia ante pérdida de señal en Huaquechula (lag de red).
    - Curva de velocidad de ingesta por minuto/hora.
    - Historial de los últimos eventos de ingesta en campo.
    - Distribución por barrio / localidad.
    GET /api/monitoring/live-stream/
    """
    t0 = time.time()
    db_ok = True
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
    except Exception:
        db_ok = False
    latency_ms = round((time.time() - t0) * 1000, 2)

    current_year = str(timezone.now().year)

    # 1. Totales de encuestas reales
    total_visitantes = EncuestaVisitante.objects.count()
    total_residentes = EncuestaResidente.objects.count()
    total_institucionales = EncuestaInstitucional.objects.count()
    total_comercios = EncuestaComercio.objects.count()
    total_visitas = RegistroVisita.objects.count()
    total_encuestas = total_visitantes + total_residentes + total_institucionales + total_comercios

    # 2. Reconciliación con indicadores
    med_57 = Medicion.objects.filter(indicador_id=57, periodo=current_year).first()
    med_34 = Medicion.objects.filter(indicador_id=34, periodo=current_year).first()
    pipeline_status = "healthy"
    sync_warnings = []
    if total_visitantes > 0 and not med_57:
        pipeline_status = "warning"
        sync_warnings.append("Falta cálculo de medición de satisfacción (ID 57).")
    if total_residentes > 0 and not med_34:
        pipeline_status = "warning"
        sync_warnings.append("Falta cálculo de medición de tensión local (ID 34).")

    # 3. Métricas de resiliencia de red (Lag por cobertura celular)
    total_audited = RegistroIngestaEncuesta.objects.count()
    total_offline = RegistroIngestaEncuesta.objects.filter(es_offline=True).count()
    total_realtime = RegistroIngestaEncuesta.objects.filter(es_offline=False).count()

    # Histogramas de retardo
    instantaneas = RegistroIngestaEncuesta.objects.filter(lag_segundos__lt=15.0).count()
    rezago_ligero = RegistroIngestaEncuesta.objects.filter(lag_segundos__gte=15.0, lag_segundos__lt=120.0).count()
    rezago_moderado = RegistroIngestaEncuesta.objects.filter(lag_segundos__gte=120.0, lag_segundos__lt=900.0).count()
    rezago_alto = RegistroIngestaEncuesta.objects.filter(lag_segundos__gte=900.0).count()

    agg_lag = RegistroIngestaEncuesta.objects.filter(es_offline=True).aggregate(
        avg_lag=Avg('lag_segundos'),
        max_lag=Max('lag_segundos')
    )
    avg_lag_sec = round(agg_lag.get('avg_lag') or 0.0, 1)
    max_lag_sec = round(agg_lag.get('max_lag') or 0.0, 1)

    # 4. Últimos 35 eventos en vivo
    recent_qs = RegistroIngestaEncuesta.objects.order_by('-fecha_ingesta')[:35]
    events = []
    for r in recent_qs:
        mins_ago = round((timezone.now() - r.fecha_ingesta).total_seconds() / 60, 1)
        events.append({
            "id": r.id,
            "tipo": r.tipo_encuesta,
            "tipo_label": r.get_tipo_encuesta_display(),
            "id_encuesta": r.id_encuesta,
            "encuestador": r.encuestador_username,
            "barrio": r.barrio_localidad or 'Cabecera / General',
            "lag_segundos": round(r.lag_segundos, 1),
            "es_offline": r.es_offline,
            "latencia_db_ms": round(r.latencia_db_ms, 1),
            "timestamp": r.fecha_ingesta.strftime("%H:%M:%S"),
            "minutos_atras": mins_ago,
            "estado": r.estado
        })

    # 5. Distribución por barrio / zona
    top_barrios = list(
        RegistroIngestaEncuesta.objects.exclude(barrio_localidad='')
        .values('barrio_localidad')
        .annotate(total=Count('id'))
        .order_by('-total')[:6]
    )

    return JsonResponse({
        "pipeline_status": pipeline_status,
        "database_connected": db_ok,
        "database_latency_ms": latency_ms,
        "server_time": timezone.now().strftime("%Y-%m-%d %H:%M:%S"),
        "summary": {
            "total_encuestas": total_encuestas,
            "visitantes": total_visitantes,
            "residentes": total_residentes,
            "institucionales": total_institucionales,
            "comercios": total_comercios,
            "registros_visita": total_visitas,
        },
        "resilience_metrics": {
            "total_auditados": total_audited,
            "en_tiempo_real": total_realtime,
            "recuperadas_offline": total_offline,
            "promedio_lag_segundos": avg_lag_sec,
            "maximo_lag_segundos": max_lag_sec,
            "lag_distribution": {
                "instantaneas": instantaneas,
                "ligero_15s_2m": rezago_ligero,
                "moderado_2m_15m": rezago_moderado,
                "alto_mas_15m": rezago_alto,
            }
        },
        "top_barrios": top_barrios,
        "recent_events": events,
        "sync_warnings": sync_warnings,
    })


@require_GET
def api_prometheus_metrics(request):
    """
    Expositor estándar OpenMetrics / Prometheus para Grafana Cloud o Grafana local.
    GET /api/metrics/
    """
    t0 = time.time()
    db_ok = 1
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
    except Exception:
        db_ok = 0
    db_latency = round(time.time() - t0, 4)

    total_v = EncuestaVisitante.objects.count()
    total_r = EncuestaResidente.objects.count()
    total_i = EncuestaInstitucional.objects.count()
    total_c = EncuestaComercio.objects.count()
    total_visitas = RegistroVisita.objects.count()

    total_audited = RegistroIngestaEncuesta.objects.count()
    total_offline = RegistroIngestaEncuesta.objects.filter(es_offline=True).count()
    total_realtime = RegistroIngestaEncuesta.objects.filter(es_offline=False).count()

    agg_lag = RegistroIngestaEncuesta.objects.filter(es_offline=True).aggregate(
        avg_lag=Avg('lag_segundos'),
        max_lag=Max('lag_segundos')
    )
    avg_lag = round(agg_lag.get('avg_lag') or 0.0, 2)
    max_lag = round(agg_lag.get('max_lag') or 0.0, 2)

    current_year = str(timezone.now().year)
    has_med_57 = 1 if Medicion.objects.filter(indicador_id=57, periodo=current_year).exists() else 0
    has_med_34 = 1 if Medicion.objects.filter(indicador_id=34, periodo=current_year).exists() else 0

    lines = [
        "# HELP huaquechula_surveys_total Total de encuestas registradas por tipo",
        "# TYPE huaquechula_surveys_total counter",
        f'huaquechula_surveys_total{{tipo="visitante"}} {total_v}',
        f'huaquechula_surveys_total{{tipo="residente"}} {total_r}',
        f'huaquechula_surveys_total{{tipo="institucional"}} {total_i}',
        f'huaquechula_surveys_total{{tipo="comercio"}} {total_c}',
        f'huaquechula_surveys_total{{tipo="conteo_visita"}} {total_visitas}',
        "",
        "# HELP huaquechula_network_resilience_events Eventos de ingesta analizados por resiliencia de red",
        "# TYPE huaquechula_network_resilience_events counter",
        f'huaquechula_network_resilience_events{{status="realtime"}} {total_realtime}',
        f'huaquechula_network_resilience_events{{status="offline_buffered"}} {total_offline}',
        f'huaquechula_network_resilience_events{{status="total_audited"}} {total_audited}',
        "",
        "# HELP huaquechula_network_lag_seconds Rezago temporal en segundos por desconexion en campo",
        "# TYPE huaquechula_network_lag_seconds gauge",
        f'huaquechula_network_lag_seconds{{metric="promedio"}} {avg_lag}',
        f'huaquechula_network_lag_seconds{{metric="maximo"}} {max_lag}',
        "",
        "# HELP huaquechula_database_latency_seconds Latencia de respuesta de PostgreSQL",
        "# TYPE huaquechula_database_latency_seconds gauge",
        f"huaquechula_database_latency_seconds {db_latency}",
        "",
        "# HELP huaquechula_database_connected Estado de conexion a la base de datos (1=ok, 0=error)",
        "# TYPE huaquechula_database_connected gauge",
        f"huaquechula_database_connected {db_ok}",
        "",
        "# HELP huaquechula_indicator_reconciled Estado de reconciliacion de indicadores clave (1=ok)",
        "# TYPE huaquechula_indicator_reconciled gauge",
        f'huaquechula_indicator_reconciled{{indicador="satisfaccion_57"}} {has_med_57}',
        f'huaquechula_indicator_reconciled{{indicador="tension_34"}} {has_med_34}',
        ""
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain; version=0.0.4; charset=utf-8")

