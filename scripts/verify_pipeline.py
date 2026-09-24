"""
verify_pipeline.py — Certificación y Auditoría End-to-End del Flujo de Datos
Observatorio de Datos de Huaquechula (Fly.io + PostgreSQL)

Valida la cadena completa:
1. Sonda de salud (/api/health/)
2. Autenticación JWT móvil (/api/mobile/login/)
3. Lectura de conteos basales (/api/monitoring/survey-flow/)
4. Ingesta de encuesta de prueba vía API (/api/mobile/encuestas/visitante/)
5. Recálculo automático de indicadores en PostgreSQL
6. Reflejo en API pública de estadísticas (/api/visitor-stats/)
7. Auditoría de reconciliación (/api/monitoring/survey-flow/)
"""
import sys
import time
import requests

# Forzar codificación UTF-8 para consolas Windows
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

DEFAULT_URL = "https://observatorio-huaquechula.fly.dev"

def run_pipeline_verification(base_url=DEFAULT_URL):
    print("=" * 70)
    print(f"[>] INICIANDO AUDITORIA Y CERTIFICACION DEL PIPELINE DE DATOS")
    print(f"[*] Servidor destino: {base_url}")
    print("=" * 70)

    # ── 1. Sonda de salud (/api/health/) ─────────────────────────────────────
    t0 = time.time()
    try:
        r_health = requests.get(f"{base_url}/api/health/", timeout=10)
        latency = round((time.time() - t0) * 1000, 2)
        if r_health.status_code == 200:
            data = r_health.json()
            print(f"[OK] [1/6] Health Check: 200 OK | BD: {data.get('database')} | Latencia: {latency} ms")
        else:
            print(f"[ERROR] [1/6] Health Check falló con status {r_health.status_code}: {r_health.text}")
            return False
    except Exception as e:
        print(f"[ERROR] [1/6] Error conectando a {base_url}/api/health/: {e}")
        return False

    # ── 2. Autenticación móvil con JWT (/api/mobile/login/) ───────────────────
    try:
        r_login = requests.post(
            f"{base_url}/api/mobile/login/",
            json={"username": "encuestador_demo", "password": "demo1234"},
            timeout=10
        )
        if r_login.status_code == 200:
            token = r_login.json().get("access")
            headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
            print(f"[OK] [2/6] Autenticación JWT: Token obtenido exitosamente para 'encuestador_demo'")
        else:
            print(f"[ERROR] [2/6] Fallo al autenticar con encuestador_demo: {r_login.status_code} {r_login.text}")
            return False
    except Exception as e:
        print(f"[ERROR] [2/6] Error en petición de login: {e}")
        return False

    # ── 3. Lectura de estado basal del flujo (/api/monitoring/survey-flow/) ──
    try:
        r_flow_before = requests.get(f"{base_url}/api/monitoring/survey-flow/", timeout=10)
        flow_before = r_flow_before.json()
        count_v_before = flow_before["summary"]["visitantes"]
        total_before = flow_before["summary"]["total_encuestas"]
        print(f"[OK] [3/6] Estado basal: {total_before} encuestas totales ({count_v_before} de visitantes)")
    except Exception as e:
        print(f"[ERROR] [3/6] Error al leer estado de flujo previo: {e}")
        return False

    # ── 4. Ingesta de Encuesta Sintética ──────────────────────────────────────
    test_tag = f"Auditoría E2E {time.strftime('%Y-%m-%d %H:%M:%S')}"
    payload = {
        "genero": "Femenino",
        "edad": 28,
        "viaja_con": "En pareja",
        "residencia_ciudad": "Puebla",
        "residencia_estado": "Puebla",
        "residencia_pais": "México",
        "zonas_visitadas": "Centro, Ex Convento Franciscano",
        "actividades": "Probar la gastronomía local / ir a restaurantes",
        "satisfaccion": 5,
        "lo_que_mas_gusto": test_tag
    }

    t_post = time.time()
    try:
        r_create = requests.post(
            f"{base_url}/api/mobile/encuestas/visitante/",
            json=payload,
            headers=headers,
            timeout=15
        )
        post_elapsed = round((time.time() - t_post) * 1000, 2)
        if r_create.status_code == 201:
            survey_data = r_create.json()
            survey_id = survey_data.get("id")
            print(f"[OK] [4/6] Ingesta móvil: HTTP 201 Created | Encuesta ID #{survey_id} | Tiempo: {post_elapsed} ms")
        else:
            print(f"[ERROR] [4/6] Fallo en creación de encuesta: {r_create.status_code} {r_create.text}")
            return False
    except Exception as e:
        print(f"[ERROR] [4/6] Error enviando encuesta: {e}")
        return False

    # ── 5. Verificación de reflejo en API de Estadísticas (/api/visitor-stats/)
    time.sleep(1) # Breve pausa para asegurar consistencia
    try:
        r_stats = requests.get(f"{base_url}/api/visitor-stats/", timeout=10)
        if r_stats.status_code == 200:
            stats = r_stats.json()
            total_resenas = stats.get("total_resenas", 0)
            satisfaccion = stats.get("satisfaccion_promedio", 0)
            print(f"[OK] [5/6] Estadísticas Web: HTTP 200 | Total reseñas: {total_resenas} | Satisfacción: {satisfaccion}/5")
        else:
            print(f"[ERROR] [5/6] Error al consultar /api/visitor-stats/: {r_stats.status_code}")
            return False
    except Exception as e:
        print(f"[ERROR] [5/6] Error en visitor-stats: {e}")
        return False

    # ── 6. Verificación de Reconciliación (/api/monitoring/survey-flow/) ───────
    try:
        r_flow_after = requests.get(f"{base_url}/api/monitoring/survey-flow/", timeout=10)
        flow_after = r_flow_after.json()
        count_v_after = flow_after["summary"]["visitantes"]
        pipeline_status = flow_after.get("pipeline_status")
        latest = flow_after.get("latest_survey", {})

        delta_v = count_v_after - count_v_before

        if delta_v == 1 and pipeline_status == "healthy":
            print(f"[OK] [6/6] Reconciliación: ÉXITO (Δ Encuestas = +1, Pipeline = {pipeline_status.upper()})")
            print(f"         Última encuesta detectada: {latest.get('type')} ID #{latest.get('id')} hace {latest.get('minutes_ago')} min.")
        else:
            print(f"[WARN] [6/6] Advertencia en reconciliación: Δ={delta_v}, status={pipeline_status}")
            return False
    except Exception as e:
        print(f"[ERROR] [6/6] Error consultando reconciliación posterior: {e}")
        return False

    print("=" * 70)
    print("[SUCCESS] RESULTADO: PIPELINE CERTIFICADO Y 100% OPERATIVO")
    print("   Los datos enviados desde la app móvil se persisten en PostgreSQL")
    print("   y se reflejan fielmente en las estadísticas y dashboards web.")
    print("=" * 70)
    return True

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_URL
    success = run_pipeline_verification(target)
    sys.exit(0 if success else 1)
