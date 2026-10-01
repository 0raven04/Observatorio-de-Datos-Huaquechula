#!/usr/bin/env python3
"""
Test de Carga y Rendimiento Concurrente — Observatorio Huaquechula
Evalúa la resiliencia, latencia y rendimiento (RPS) de los endpoints críticos
bajo diferentes niveles de concurrencia simulando la afluencia de Todos Santos.
"""

import sys
import ssl
import time
import json
import statistics
import urllib.request
import urllib.error
from concurrent.futures import ThreadPoolExecutor, as_completed

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

SSL_CTX = ssl._create_unverified_context()
BASE_URL = "https://observatorio-huaquechula.fly.dev"

SCENARIOS = [
    {
        "id": "health_baseline",
        "name": "Línea Base: Endpoint de Salud (Health Check)",
        "url": f"{BASE_URL}/api/health/",
        "method": "GET",
        "total_requests": 50,
        "concurrency": 10,
        "description": "Verifica latencia de red base y sobrecarga mínima del servidor."
    },
    {
        "id": "circuit_normal",
        "name": "Cálculo de Circuito Turístico TSP (Concurrencia Moderada)",
        "url": f"{BASE_URL}/api/gis/circuito-turistico/?categoria=todos&inicio=zocalo",
        "method": "GET",
        "total_requests": 60,
        "concurrency": 15,
        "description": "Evalúa ejecución algorítmica de 2-Opt TSP con 11 puntos y 15 usuarios concurrentes."
    },
    {
        "id": "circuit_peak",
        "name": "Cálculo de Circuito Turístico TSP (Ráfaga Pico Todos Santos)",
        "url": f"{BASE_URL}/api/gis/circuito-turistico/?categoria=ofrenda&inicio=zocalo",
        "method": "GET",
        "total_requests": 100,
        "concurrency": 30,
        "description": "Simula ráfaga simultánea de visitantes consultando circuitos de altares en el Zócalo."
    },
    {
        "id": "dashboard_ssr",
        "name": "Dashboard del Observatorio (Server-Side Rendering)",
        "url": f"{BASE_URL}/dashboard/",
        "method": "GET",
        "total_requests": 40,
        "concurrency": 10,
        "description": "Evalúa renderizado de Django con agregación de 3 ejes y múltiples indicadores."
    },
    {
        "id": "visitor_stats_api",
        "name": "API de Estadísticas de Afluencia y Reseñas",
        "url": f"{BASE_URL}/api/visitor-stats/",
        "method": "GET",
        "total_requests": 50,
        "concurrency": 15,
        "description": "Consulta de métricas agregadas de visitantes y calificaciones en tiempo real."
    }
]

def make_request(url, method="GET", timeout=15):
    """Realiza una petición HTTP cronometrada con urllib."""
    start_time = time.perf_counter()
    status_code = 0
    error_msg = None
    response_size = 0

    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "HuaquechulaBenchmark/1.0 (StressTestBot; LoadRunner)",
            "Accept": "application/json, text/html, */*"
        },
        method=method
    )

    try:
        with urllib.request.urlopen(req, timeout=timeout, context=SSL_CTX) as resp:
            data = resp.read()
            status_code = resp.status
            response_size = len(data)
    except urllib.error.HTTPError as e:
        status_code = e.code
        error_msg = f"HTTP {e.code}: {e.reason}"
    except urllib.error.URLError as e:
        status_code = 0
        error_msg = f"URLError: {e.reason}"
    except Exception as e:
        status_code = 0
        error_msg = f"Exception: {str(e)}"

    duration_ms = (time.perf_counter() - start_time) * 1000.0
    return {
        "status_code": status_code,
        "duration_ms": duration_ms,
        "success": 200 <= status_code < 300,
        "error": error_msg,
        "bytes": response_size
    }

def run_scenario(scenario):
    name = scenario["name"]
    url = scenario["url"]
    total = scenario["total_requests"]
    workers = scenario["concurrency"]

    print(f"\n{'='*75}")
    print(f" > Ejecutando: {name}")
    print(f"   URL: {url}")
    print(f"   Peticiones: {total} | Concurrencia: {workers} workers simultaneos")
    print(f"{'='*75}")

    latencies = []
    success_count = 0
    failure_count = 0
    errors = {}
    total_bytes = 0

    benchmark_start = time.perf_counter()

    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = [executor.submit(make_request, url, scenario["method"]) for _ in range(total)]
        completed = 0

        for f in as_completed(futures):
            res = f.result()
            completed += 1
            latencies.append(res["duration_ms"])
            total_bytes += res["bytes"]

            if res["success"]:
                success_count += 1
            else:
                failure_count += 1
                err = res["error"] or f"HTTP {res['status_code']}"
                errors[err] = errors.get(err, 0) + 1

            if completed % max(1, total // 5) == 0 or completed == total:
                pct = int((completed / total) * 100)
                print(f"   [Progreso: {pct:3d}%] {completed}/{total} completadas...")

    benchmark_elapsed = time.perf_counter() - benchmark_start
    rps = total / benchmark_elapsed if benchmark_elapsed > 0 else 0

    latencies.sort()
    min_lat = min(latencies) if latencies else 0
    max_lat = max(latencies) if latencies else 0
    mean_lat = statistics.mean(latencies) if latencies else 0
    median_lat = statistics.median(latencies) if latencies else 0
    stdev_lat = statistics.stdev(latencies) if len(latencies) > 1 else 0

    def percentile(p):
        if not latencies:
            return 0
        idx = int(len(latencies) * p)
        return latencies[min(idx, len(latencies) - 1)]

    p90 = percentile(0.90)
    p95 = percentile(0.95)
    p99 = percentile(0.99)

    result = {
        "scenario_id": scenario["id"],
        "name": name,
        "url": url,
        "total_requests": total,
        "concurrency": workers,
        "total_time_sec": round(benchmark_elapsed, 2),
        "requests_per_sec": round(rps, 2),
        "success_count": success_count,
        "failure_count": failure_count,
        "success_rate_pct": round((success_count / total) * 100, 2),
        "total_kb_transferred": round(total_bytes / 1024.0, 2),
        "latency_min_ms": round(min_lat, 2),
        "latency_max_ms": round(max_lat, 2),
        "latency_mean_ms": round(mean_lat, 2),
        "latency_median_ms": round(median_lat, 2),
        "latency_stdev_ms": round(stdev_lat, 2),
        "latency_p90_ms": round(p90, 2),
        "latency_p95_ms": round(p95, 2),
        "latency_p99_ms": round(p99, 2),
        "errors": errors
    }

    print(f"\n   [OK] Exito: {success_count}/{total} ({result['success_rate_pct']}%)")
    print(f"   [TIME] Tiempo Total: {result['total_time_sec']}s | Throughput: {result['requests_per_sec']} req/s")
    print(f"   [STATS] Latencias: Min: {result['latency_min_ms']}ms | Promedio: {result['latency_mean_ms']}ms | Mediana (p50): {result['latency_median_ms']}ms")
    print(f"   [PERCENTILES] p90: {result['latency_p90_ms']}ms | p95: {result['latency_p95_ms']}ms | Max: {result['latency_max_ms']}ms")

    if errors:
        print(f"   [WARN] Errores detectados: {errors}")

    return result

def main():
    print("""
===========================================================================
  OBSERVATORIO DE DATOS HUAQUECHULA — PRUEBA DE ESTRÉS Y RENDIMIENTO
  Objetivo: Certificación de Capacidad de Concurrencia para Todos Santos
  Entorno: https://observatorio-huaquechula.fly.dev
===========================================================================
    """)

    all_results = []
    for sc in SCENARIOS:
        try:
            res = run_scenario(sc)
            all_results.append(res)
            time.sleep(1) # Pequeño enfriamiento entre escenarios
        except Exception as e:
            print(f"ERROR en escenario {sc['name']}: {e}")

    summary_file = "scripts/benchmark_results.json"
    with open(summary_file, "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)

    print(f"\nResultados completos guardados en: {summary_file}")

if __name__ == "__main__":
    main()
