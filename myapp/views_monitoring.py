"""
views_monitoring.py — Endpoints de auditoría, observabilidad y alertas del flujo de datos.
Permite verificar en tiempo real que las encuestas móviles lleguen a PostgreSQL y se reflejen en la web.
"""
import os
import time
import json
import logging
import requests
from django.http import JsonResponse
from django.utils import timezone
from django.db import connection
from django.views.decorators.http import require_GET, require_POST
from django.views.decorators.csrf import csrf_exempt

from .models import (
    EncuestaVisitante, EncuestaResidente, EncuestaInstitucional,
    EncuestaComercio, RegistroVisita, Medicion, Indicador
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
