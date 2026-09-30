import math
import json
import logging
from typing import List, Dict, Any, Tuple, Optional

logger = logging.getLogger(__name__)

# Coordenadas por defecto: Zócalo de Huaquechula, Puebla
DEFAULT_ORIGIN_LAT = 18.769895
DEFAULT_ORIGIN_LNG = -98.544040

# Velocidad peatonal turística promedio en terreno urbano/rural (km/h)
VELOCIDAD_PEATONAL_KMH = 4.2

# Factor de sinuosidad urbana (las calles peatonales no son líneas rectas, distancia real ~ 1.25x la geodésica)
FACTOR_SINUOSIDAD_CALLES = 1.28

# Tiempo promedio sugerido de estancia/visita por parada (minutos)
TIEMPO_ESTANCIA_POR_PARADA_MIN = 15


def distancia_haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calcula la distancia geodésica en metros entre dos coordenadas (WGS84).
    """
    R = 6371000.0  # Radio medio de la Tierra en metros
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (math.sin(delta_phi / 2.0) ** 2 +
         math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2)
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return R * c


def estimar_distancia_calle_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Estima la distancia real a pie considerando la red de calles mediante factor de sinuosidad.
    """
    geodesica = distancia_haversine(lat1, lon1, lat2, lon2)
    return round(geodesica * FACTOR_SINUOSIDAD_CALLES, 1)


def estimar_tiempo_caminata_min(distancia_m: float) -> int:
    """
    Calcula los minutos de caminata a velocidad turística (~4.2 km/h).
    """
    horas = (distancia_m / 1000.0) / VELOCIDAD_PEATONAL_KMH
    return max(1, math.ceil(horas * 60))


def resolver_tsp_2opt(nodos: List[Dict[str, Any]], circuito_cerrado: bool = True) -> Tuple[List[Dict[str, Any]], float]:
    """
    Resuelve el Traveling Salesperson Problem (TSP) para una lista de nodos.
    El nodo 0 es siempre el punto de partida (origen).
    Utiliza la heurística Nearest Neighbor seguida de optimización local 2-Opt.
    Garantiza que las rutas no se crucen y minimiza la distancia total de caminata.
    """
    num_nodos = len(nodos)
    if num_nodos <= 2:
        dist_total = 0.0
        for i in range(num_nodos - 1):
            dist_total += estimar_distancia_calle_m(
                nodos[i]['lat'], nodos[i]['lng'],
                nodos[i + 1]['lat'], nodos[i + 1]['lng']
            )
        if circuito_cerrado and num_nodos == 2:
            dist_total += estimar_distancia_calle_m(
                nodos[1]['lat'], nodos[1]['lng'],
                nodos[0]['lat'], nodos[0]['lng']
            )
        return nodos, dist_total

    # Matriz de distancias
    dist_matrix = [[0.0] * num_nodos for _ in range(num_nodos)]
    for i in range(num_nodos):
        for j in range(i + 1, num_nodos):
            d = estimar_distancia_calle_m(
                nodos[i]['lat'], nodos[i]['lng'],
                nodos[j]['lat'], nodos[j]['lng']
            )
            dist_matrix[i][j] = d
            dist_matrix[j][i] = d

    # 1. Construcción inicial con Nearest Neighbor partiendo del nodo 0
    visitados = [False] * num_nodos
    ruta_indices = [0]
    visitados[0] = True

    nodo_actual = 0
    for _ in range(num_nodos - 1):
        siguiente_nodo = None
        menor_dist = float('inf')
        for candidato in range(num_nodos):
            if not visitados[candidato]:
                if dist_matrix[nodo_actual][candidato] < menor_dist:
                    menor_dist = dist_matrix[nodo_actual][candidato]
                    siguiente_nodo = candidato
        if siguiente_nodo is not None:
            ruta_indices.append(siguiente_nodo)
            visitados[siguiente_nodo] = True
            nodo_actual = siguiente_nodo

    def calcular_costo_ruta(indices: List[int]) -> float:
        costo = 0.0
        for idx in range(len(indices) - 1):
            costo += dist_matrix[indices[idx]][indices[idx + 1]]
        if circuito_cerrado:
            costo += dist_matrix[indices[-1]][indices[0]]
        return costo

    # 2. Optimización 2-Opt
    mejor_costo = calcular_costo_ruta(ruta_indices)
    mejora = True
    max_iteraciones = 150
    iter_actual = 0

    while mejora and iter_actual < max_iteraciones:
        mejora = False
        iter_actual += 1

        # El nodo 0 es fijo (origen). Iteramos sobre los demás nodos (1 a n-1)
        for i in range(1, num_nodos - 1):
            for j in range(i + 1, num_nodos):
                # Proponer invertir el subsegmento [i, j]
                nueva_ruta = ruta_indices[:i] + ruta_indices[i:j + 1][::-1] + ruta_indices[j + 1:]
                nuevo_costo = calcular_costo_ruta(nueva_ruta)
                if nuevo_costo < mejor_costo - 0.01:
                    ruta_indices = nueva_ruta
                    mejor_costo = nuevo_costo
                    mejora = True
                    break
            if mejora:
                break

    # Reordenar nodos según la ruta óptima encontrada
    nodos_ordenados = [nodos[idx] for idx in ruta_indices]
    return nodos_ordenados, round(mejor_costo, 1)


def extraer_coordenadas_de_geometria(geo) -> Optional[Tuple[float, float]]:
    """
    Extrae (latitud, longitud) de un objeto GeometriaEspacial.
    Maneja geometrías tipo punto, línea o polígono extrayendo el centroide.
    """
    if not geo or not geo.coordenadas:
        return None

    try:
        raw = geo.coordenadas if isinstance(geo.coordenadas, (dict, list)) else json.loads(geo.coordenadas)
        if isinstance(raw, dict) and 'coordinates' in raw:
            coords = raw['coordinates']
        else:
            coords = raw

        if geo.tipo == 'punto':
            # GeoJSON almacena [longitud, latitud]
            if isinstance(coords, list) and len(coords) >= 2:
                lng, lat = float(coords[0]), float(coords[1])
                return lat, lng
        elif geo.tipo in ('poligono', 'multipoligono', 'linea'):
            # Calcular centroide simple para polígonos/líneas
            puntos = []
            def _aplanar(c):
                if isinstance(c, list) and len(c) >= 2 and isinstance(c[0], (int, float)):
                    puntos.append((float(c[1]), float(c[0])))
                elif isinstance(c, list):
                    for sub in c:
                        _aplanar(sub)
            _aplanar(coords)
            if puntos:
                avg_lat = sum(p[0] for p in puntos) / len(puntos)
                avg_lng = sum(p[1] for p in puntos) / len(puntos)
                return avg_lat, avg_lng
    except Exception as e:
        logger.warning(f"Error extrayendo coordenadas de geometría {getattr(geo, 'id_geometria', None)}: {e}")

    return None


def generar_circuito_turistico(
    categoria: str = 'ofrenda',
    puntos_ids: Optional[List[int]] = None,
    origen_lat: Optional[float] = None,
    origen_lng: Optional[float] = None,
    origen_nombre: str = "Punto de Partida",
    circuito_cerrado: bool = True,
    max_paradas: int = 15
) -> Dict[str, Any]:
    """
    Servicio principal para cálculo de Circuitos Turísticos Inteligentes.
    Encuentra los puntos elegibles, optimiza la ruta con TSP (2-Opt) y genera
    métricas de distancia, tiempos de caminata y estancia recomendada.
    """
    from myapp.models import Punto_Interes

    lat_inicio = origen_lat if origen_lat is not None else DEFAULT_ORIGIN_LAT
    lng_inicio = origen_lng if origen_lng is not None else DEFAULT_ORIGIN_LNG

    # 1. Consultar puntos de interés elegibles
    query = Punto_Interes.objects.filter(estado='activo', id_geometria__isnull=False).select_related(
        'id_geometria', 'sitio_turistico', 'ofrenda', 'servicio'
    ).prefetch_related('galeria_multimedia_set')

    if puntos_ids:
        query = query.filter(id_punto__in=puntos_ids)
    elif categoria and categoria != 'todos':
        query = query.filter(categoria=categoria)

    candidatos = list(query)
    if not candidatos:
        return {
            "status": "empty",
            "mensaje": f"No se encontraron puntos de interés activos para la categoría '{categoria}'.",
            "paradas": [],
            "resumen": {}
        }

    # 2. Formatear nodos para el optimizador
    nodos_destino = []
    for p in candidatos:
        coords = extraer_coordenadas_de_geometria(p.id_geometria)
        if not coords:
            continue

        lat, lng = coords
        
        # Anfitrión para ofrendas
        anfitrion = ""
        if hasattr(p, 'ofrenda') and p.ofrenda:
            anfitrion = p.ofrenda.anfitrion or ""

        # Imagen de portada o primera de galería
        imagen_url = ""
        if p.imagen_portada:
            imagen_url = getattr(p.imagen_portada, 'url', str(p.imagen_portada))
        elif p.galeria_multimedia_set.exists():
            primera = p.galeria_multimedia_set.first()
            if primera:
                imagen_url = primera.url_archivo

        nodos_destino.append({
            "id_punto": p.id_punto,
            "nombre": p.nombre,
            "categoria": p.categoria,
            "categoria_display": p.get_categoria_display() if hasattr(p, 'get_categoria_display') else p.categoria.title(),
            "anfitrion": anfitrion,
            "descripcion": (p.descripcion or "")[:150],
            "imagen": imagen_url,
            "lat": lat,
            "lng": lng,
            "es_origen": False
        })

    if not nodos_destino:
        return {
            "status": "error",
            "mensaje": "Los puntos seleccionados no cuentan con coordenadas espaciales válidas.",
            "paradas": [],
            "resumen": {}
        }

    # Limitar paradas si se especificó
    if len(nodos_destino) > max_paradas:
        # Ordenar por proximidad al origen antes de recortar para no dejar puntos demasiado alejados
        nodos_destino.sort(key=lambda n: distancia_haversine(lat_inicio, lng_inicio, n['lat'], n['lng']))
        nodos_destino = nodos_destino[:max_paradas]

    # Nodo 0: Origen
    nodo_origen = {
        "id_punto": 0,
        "nombre": origen_nombre,
        "categoria": "origen",
        "categoria_display": "Punto de Partida",
        "anfitrion": "",
        "descripcion": "Inicio del circuito turístico",
        "imagen": "",
        "lat": lat_inicio,
        "lng": lng_inicio,
        "es_origen": True
    }

    todos_los_nodos = [nodo_origen] + nodos_destino

    # 3. Resolver TSP
    nodos_optimizados, distancia_total_m = resolver_tsp_2opt(todos_los_nodos, circuito_cerrado=circuito_cerrado)

    # 4. Construir tramos paso a paso
    paradas = []
    distancia_acumulada_m = 0.0
    waypoints_coordenadas = []

    for idx, nodo in enumerate(nodos_optimizados):
        waypoints_coordenadas.append([nodo['lat'], nodo['lng']])

        dist_tramo = 0.0
        tiempo_tramo = 0
        if idx < len(nodos_optimizados) - 1:
            siguiente = nodos_optimizados[idx + 1]
            dist_tramo = estimar_distancia_calle_m(nodo['lat'], nodo['lng'], siguiente['lat'], siguiente['lng'])
            tiempo_tramo = estimar_tiempo_caminata_min(dist_tramo)
        elif circuito_cerrado and len(nodos_optimizados) > 1:
            # Tramo final de vuelta al origen
            siguiente = nodos_optimizados[0]
            dist_tramo = estimar_distancia_calle_m(nodo['lat'], nodo['lng'], siguiente['lat'], siguiente['lng'])
            tiempo_tramo = estimar_tiempo_caminata_min(dist_tramo)

        distancia_acumulada_m += dist_tramo

        paradas.append({
            "orden": idx,  # 0 es origen, 1, 2, ... son paradas
            "es_origen": nodo.get("es_origen", False),
            "id_punto": nodo["id_punto"],
            "nombre": nodo["nombre"],
            "categoria": nodo["categoria"],
            "categoria_display": nodo["categoria_display"],
            "anfitrion": nodo["anfitrion"],
            "descripcion": nodo["descripcion"],
            "imagen": nodo["imagen"],
            "lat": nodo["lat"],
            "lng": nodo["lng"],
            "distancia_siguiente_m": dist_tramo,
            "tiempo_siguiente_min": tiempo_tramo
        })

    # Si es cerrado, cerrar también los waypoints
    if circuito_cerrado and len(waypoints_coordenadas) > 1:
        waypoints_coordenadas.append(waypoints_coordenadas[0])

    num_sitios_visita = len(nodos_destino)
    tiempo_caminata_total_min = estimar_tiempo_caminata_min(distancia_total_m)
    tiempo_estancia_total_min = num_sitios_visita * TIEMPO_ESTANCIA_POR_PARADA_MIN
    tiempo_total_min = tiempo_caminata_total_min + tiempo_estancia_total_min

    # Estimación de pasos (promedio ~0.75m por paso)
    pasos_estimados = int(distancia_total_m / 0.75)

    resumen = {
        "total_paradas": num_sitios_visita,
        "distancia_total_m": distancia_total_m,
        "distancia_total_km": round(distancia_total_m / 1000.0, 2),
        "tiempo_caminata_min": tiempo_caminata_total_min,
        "tiempo_estancia_min": tiempo_estancia_total_min,
        "tiempo_total_min": tiempo_total_min,
        "tiempo_total_formato": f"{tiempo_total_min // 60}h {tiempo_total_min % 60}m" if tiempo_total_min >= 60 else f"{tiempo_total_min} min",
        "pasos_estimados": pasos_estimados,
        "circuito_cerrado": circuito_cerrado,
        "origen_lat": lat_inicio,
        "origen_lng": lng_inicio
    }

    return {
        "status": "success",
        "categoria": categoria,
        "resumen": resumen,
        "paradas": paradas,
        "waypoints": waypoints_coordenadas
    }
