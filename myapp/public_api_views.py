"""
Vistas de la API Pública Open Data — Observatorio de Datos Huaquechula.
Todos los endpoints son de solo lectura y no requieren autenticación JWT.
"""
import csv
from django.http import HttpResponse
from django.db.models import Avg, Count, Sum, Q
from django.db.models.functions import TruncMonth
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny

from .models import (
    Eje, CategoriaIndicador, Indicador, Medicion,
    RegistroVisita, Punto_Interes, Sitio_turistico,
    Ruta, Ofrenda, ResenaGlobal,
    EncuestaResidente, EncuestaComercio,
)
from .public_api_permissions import IsPublicAPIKeyValid, PublicAPIThrottle

FUENTE = "Observatorio Territorial de Huaquechula"
LICENCIA = "CC BY 4.0"
VERSION = "1.0"


def public_response(datos, total=None, pagina=1, pagina_size=None, siguiente=None):
    resp = {
        "status": "ok",
        "version": VERSION,
        "fuente": FUENTE,
        "licencia": LICENCIA,
    }
    if total is not None:
        resp["total"] = total
        resp["pagina"] = pagina
        resp["pagina_size"] = pagina_size
        resp["siguiente"] = siguiente
    resp["datos"] = datos
    return Response(resp)


# ─────────────────────────────────────────────────────────────────────────────
# GRUPO 1 — Indicadores Territoriales
# ─────────────────────────────────────────────────────────────────────────────

class EjesPublicView(APIView):
    """GET /api/v1/public/ejes/"""
    permission_classes = [AllowAny]
    throttle_classes = [PublicAPIThrottle]

    def get(self, request):
        ejes = Eje.objects.all()
        datos = [{"id": e.id, "nombre": e.nombre, "descripcion": e.descripcion} for e in ejes]
        return public_response(datos, total=len(datos))


class EjeDetailPublicView(APIView):
    """GET /api/v1/public/ejes/<id>/"""
    permission_classes = [AllowAny]
    throttle_classes = [PublicAPIThrottle]

    def get(self, request, pk):
        try:
            e = Eje.objects.get(pk=pk)
        except Eje.DoesNotExist:
            return Response({"status": "error", "mensaje": "Eje no encontrado"}, status=404)
        datos = {
            "id": e.id, "nombre": e.nombre, "descripcion": e.descripcion,
            "categorias": [{"id": c.id, "nombre": c.nombre} for c in e.categorias.all()],
        }
        return public_response(datos)


class CategoriasPublicView(APIView):
    """GET /api/v1/public/categorias/?eje=<id>"""
    permission_classes = [AllowAny]
    throttle_classes = [PublicAPIThrottle]

    def get(self, request):
        qs = CategoriaIndicador.objects.select_related("eje").all()
        eje_id = request.query_params.get("eje")
        if eje_id:
            qs = qs.filter(eje_id=eje_id)
        datos = [{"id": c.id, "nombre": c.nombre, "eje_id": c.eje_id, "eje": c.eje.nombre} for c in qs]
        return public_response(datos, total=len(datos))


class CategoriaDetailPublicView(APIView):
    """GET /api/v1/public/categorias/<id>/"""
    permission_classes = [AllowAny]
    throttle_classes = [PublicAPIThrottle]

    def get(self, request, pk):
        try:
            c = CategoriaIndicador.objects.select_related("eje").get(pk=pk)
        except CategoriaIndicador.DoesNotExist:
            return Response({"status": "error", "mensaje": "Categoría no encontrada"}, status=404)
        datos = {
            "id": c.id, "nombre": c.nombre,
            "eje": {"id": c.eje.id, "nombre": c.eje.nombre},
            "indicadores": [{"id": i.id, "nombre": i.nombre} for i in c.indicadores.all()],
        }
        return public_response(datos)


class IndicadoresPublicView(APIView):
    """GET /api/v1/public/indicadores/?eje=&categoria=&formato=csv"""
    permission_classes = [AllowAny]
    throttle_classes = [PublicAPIThrottle]

    def get(self, request):
        qs = Indicador.objects.select_related("categoria__eje").prefetch_related("mediciones").all()
        eje_id = request.query_params.get("eje")
        cat_id = request.query_params.get("categoria")
        if eje_id:
            qs = qs.filter(categoria__eje_id=eje_id)
        if cat_id:
            qs = qs.filter(categoria_id=cat_id)

        formato = request.query_params.get("formato", "json")
        if formato == "csv":
            return self._csv_response(qs)

        datos = [self._indicador_dict(i) for i in qs]
        return public_response(datos, total=len(datos))

    def _indicador_dict(self, i):
        ultima = i.mediciones.order_by("-periodo").first()
        return {
            "id": i.id,
            "nombre": i.nombre,
            "descripcion": i.descripcion,
            "unidad_medida": i.unidad_medida,
            "fuente": i.data_source,
            "categoria": i.categoria.nombre,
            "eje": i.categoria.eje.nombre,
            "ultima_medicion": {"periodo": ultima.periodo, "valor": str(ultima.valor)} if ultima else None,
        }

    def _csv_response(self, qs):
        resp = HttpResponse(content_type="text/csv; charset=utf-8")
        resp["Content-Disposition"] = 'attachment; filename="indicadores.csv"'
        writer = csv.writer(resp)
        writer.writerow(["id", "nombre", "unidad_medida", "eje", "categoria", "periodo", "valor"])
        for i in qs:
            for m in i.mediciones.order_by("periodo"):
                writer.writerow([i.id, i.nombre, i.unidad_medida,
                                  i.categoria.eje.nombre, i.categoria.nombre,
                                  m.periodo, m.valor])
        return resp


class IndicadorDetailPublicView(APIView):
    """GET /api/v1/public/indicadores/<id>/"""
    permission_classes = [AllowAny]
    throttle_classes = [PublicAPIThrottle]

    def get(self, request, pk):
        try:
            i = Indicador.objects.select_related("categoria__eje").get(pk=pk)
        except Indicador.DoesNotExist:
            return Response({"status": "error", "mensaje": "Indicador no encontrado"}, status=404)
        datos = {
            "id": i.id, "nombre": i.nombre, "descripcion": i.descripcion,
            "unidad_medida": i.unidad_medida, "fuente": i.data_source,
            "categoria": i.categoria.nombre, "eje": i.categoria.eje.nombre,
        }
        return public_response(datos)


class IndicadorSerieView(APIView):
    """GET /api/v1/public/indicadores/<id>/serie/"""
    permission_classes = [AllowAny]
    throttle_classes = [PublicAPIThrottle]

    def get(self, request, pk):
        try:
            i = Indicador.objects.select_related("categoria__eje").get(pk=pk)
        except Indicador.DoesNotExist:
            return Response({"status": "error", "mensaje": "Indicador no encontrado"}, status=404)
        mediciones = i.mediciones.order_by("periodo")
        datos = {
            "indicador": {
                "id": i.id, "nombre": i.nombre, "unidad": i.unidad_medida,
                "categoria": i.categoria.nombre, "eje": i.categoria.eje.nombre,
                "fuente": i.data_source,
            },
            "serie": [{"periodo": m.periodo, "valor": str(m.valor)} for m in mediciones],
        }
        return public_response(datos)


class IndicadorUltimaView(APIView):
    """GET /api/v1/public/indicadores/<id>/ultima/"""
    permission_classes = [AllowAny]
    throttle_classes = [PublicAPIThrottle]

    def get(self, request, pk):
        try:
            i = Indicador.objects.get(pk=pk)
        except Indicador.DoesNotExist:
            return Response({"status": "error", "mensaje": "Indicador no encontrado"}, status=404)
        ultima = i.mediciones.order_by("-periodo").first()
        datos = {
            "indicador_id": i.id,
            "nombre": i.nombre,
            "unidad_medida": i.unidad_medida,
            "ultima_medicion": {"periodo": ultima.periodo, "valor": str(ultima.valor)} if ultima else None,
        }
        return public_response(datos)


class IndicadorJSONStatView(APIView):
    """GET /api/v1/public/indicadores/<id>/jsonstat/ — Formato JSON-stat 2.0"""
    permission_classes = [AllowAny]
    throttle_classes = [PublicAPIThrottle]

    def get(self, request, pk):
        try:
            i = Indicador.objects.get(pk=pk)
        except Indicador.DoesNotExist:
            return Response({"status": "error", "mensaje": "Indicador no encontrado"}, status=404)
        mediciones = list(i.mediciones.order_by("periodo"))
        periodos = [m.periodo for m in mediciones]
        valores = [float(m.valor) for m in mediciones]
        datos = {
            "version": "2.0",
            "class": "dataset",
            "label": i.nombre,
            "source": FUENTE,
            "updated": i.last_sync.strftime("%Y-%m-%d") if i.last_sync else None,
            "id": ["periodo"],
            "size": [len(periodos)],
            "dimension": {
                "periodo": {
                    "label": "Período",
                    "category": {"index": {p: idx for idx, p in enumerate(periodos)}, "label": {p: p for p in periodos}},
                }
            },
            "value": valores,
        }
        return Response(datos)


# ─────────────────────────────────────────────────────────────────────────────
# GRUPO 2 — Turismo y Visitantes (datos agregados y anonimizados)
# ─────────────────────────────────────────────────────────────────────────────

def _visitas_qs(request):
    """Filtra RegistroVisita por ?año= y ?mes= si se proporcionan."""
    qs = RegistroVisita.objects.all()
    año = request.query_params.get("año")
    mes = request.query_params.get("mes")
    if año:
        qs = qs.filter(fecha__year=año)
    if mes:
        qs = qs.filter(fecha__month=mes)
    return qs


class TurismoResumenView(APIView):
    """GET /api/v1/public/turismo/resumen/"""
    permission_classes = [AllowAny]
    throttle_classes = [PublicAPIThrottle]

    def get(self, request):
        qs = _visitas_qs(request)
        total_registros = qs.count()

        total_visitantes = total_mujeres = total_hombres = suma_estancia = 0
        for r in qs:
            total_visitantes += r.total_personas
            total_mujeres += r.total_mujeres
            total_hombres += r.total_hombres
            suma_estancia += r.estancia_dias

        extranjeros = qs.filter(es_extranjero=True).count()
        datos = {
            "total_registros": total_registros,
            "total_visitantes": total_visitantes,
            "total_mujeres": total_mujeres,
            "total_hombres": total_hombres,
            "total_extranjeros": extranjeros,
            "total_nacionales": total_registros - extranjeros,
            "promedio_estancia_dias": round(suma_estancia / total_registros, 2) if total_registros else 0,
        }
        return public_response(datos)


class TurismoVisitantesPorMesView(APIView):
    """GET /api/v1/public/turismo/visitantes-por-mes/"""
    permission_classes = [AllowAny]
    throttle_classes = [PublicAPIThrottle]

    def get(self, request):
        qs = _visitas_qs(request)
        por_mes = (
            qs.annotate(mes=TruncMonth("fecha"))
            .values("mes")
            .annotate(registros=Count("id_registro"))
            .order_by("mes")
        )
        datos = [
            {"mes": item["mes"].strftime("%Y-%m"), "registros": item["registros"]}
            for item in por_mes
        ]
        return public_response(datos, total=len(datos))


class TurismoProcedenciasView(APIView):
    """GET /api/v1/public/turismo/procedencias/"""
    permission_classes = [AllowAny]
    throttle_classes = [PublicAPIThrottle]

    def get(self, request):
        qs = _visitas_qs(request)
        top = (
            qs.values("procedencia")
            .annotate(total=Count("id_registro"))
            .order_by("-total")[:20]
        )
        datos = [{"procedencia": i["procedencia"], "total": i["total"]} for i in top]
        return public_response(datos, total=len(datos))


class TurismoPerfilDemograficoView(APIView):
    """GET /api/v1/public/turismo/perfil-demografico/"""
    permission_classes = [AllowAny]
    throttle_classes = [PublicAPIThrottle]

    def get(self, request):
        qs = _visitas_qs(request)
        grupos = [
            "0_15", "16_30", "31_45", "46_60", "61_75", "76_mas"
        ]
        datos = {"mujeres": {}, "hombres": {}}
        for g in grupos:
            m_sum = qs.aggregate(v=Sum(f"mujeres_{g}"))["v"] or 0
            h_sum = qs.aggregate(v=Sum(f"hombres_{g}"))["v"] or 0
            datos["mujeres"][g] = m_sum
            datos["hombres"][g] = h_sum
        return public_response(datos)


class TurismoMotivosView(APIView):
    """GET /api/v1/public/turismo/motivos/"""
    permission_classes = [AllowAny]
    throttle_classes = [PublicAPIThrottle]

    def get(self, request):
        qs = _visitas_qs(request)
        motivos = (
            qs.values("motivo_visita")
            .annotate(total=Count("id_registro"))
            .order_by("-total")
        )
        datos = [{"motivo": i["motivo_visita"], "total": i["total"]} for i in motivos]
        return public_response(datos, total=len(datos))


class TurismoTransporteView(APIView):
    """GET /api/v1/public/turismo/transporte/"""
    permission_classes = [AllowAny]
    throttle_classes = [PublicAPIThrottle]

    def get(self, request):
        qs = _visitas_qs(request)
        transportes = (
            qs.values("tipo_transporte")
            .annotate(total=Count("id_registro"))
            .order_by("-total")
        )
        datos = [{"transporte": i["tipo_transporte"], "total": i["total"]} for i in transportes]
        return public_response(datos, total=len(datos))


class TurismoEstanciaView(APIView):
    """GET /api/v1/public/turismo/estancia/"""
    permission_classes = [AllowAny]
    throttle_classes = [PublicAPIThrottle]

    def get(self, request):
        qs = _visitas_qs(request)
        agg = qs.aggregate(promedio=Avg("estancia_dias"), max_dias=Sum("estancia_dias"))
        total = qs.count()
        datos = {
            "promedio_estancia_dias": round(agg["promedio"] or 0, 2),
            "total_registros": total,
        }
        distribucion = (
            qs.values("estancia_dias")
            .annotate(frecuencia=Count("id_registro"))
            .order_by("estancia_dias")
        )
        datos["distribucion"] = [
            {"dias": d["estancia_dias"], "frecuencia": d["frecuencia"]} for d in distribucion
        ]
        return public_response(datos)


# ─────────────────────────────────────────────────────────────────────────────
# GRUPO 3 — Territorio y Puntos de Interés (GeoJSON)
# ─────────────────────────────────────────────────────────────────────────────

def _punto_to_feature(p):
    coords = None
    if p.id_geometria and p.id_geometria.coordenadas:
        c = p.id_geometria.coordenadas
        if isinstance(c, list) and len(c) >= 2:
            coords = c
    return {
        "type": "Feature",
        "geometry": {"type": "Point", "coordinates": coords} if coords else None,
        "properties": {
            "id": p.id_punto,
            "nombre": p.nombre,
            "categoria": p.categoria,
            "descripcion": p.descripcion,
            "estado": p.estado,
            "imagen_portada": p.imagen_portada,
            "hora_apertura": str(p.hora_apertura) if p.hora_apertura else None,
            "hora_cierre": str(p.hora_cierre) if p.hora_cierre else None,
        },
    }


class PuntosInteresPublicView(APIView):
    """GET /api/v1/public/puntos-interes/?tipo=&activo=&formato=geojson"""
    permission_classes = [AllowAny]
    throttle_classes = [PublicAPIThrottle]

    def get(self, request):
        qs = Punto_Interes.objects.select_related("id_geometria").all()
        tipo = request.query_params.get("tipo")
        activo = request.query_params.get("activo")
        if tipo:
            qs = qs.filter(categoria=tipo)
        if activo is not None:
            qs = qs.filter(estado="activo" if activo.lower() in ("true", "1") else "inactivo")

        formato = request.query_params.get("formato", "json")
        if formato == "geojson":
            return Response({
                "type": "FeatureCollection",
                "fuente": FUENTE,
                "licencia": LICENCIA,
                "features": [_punto_to_feature(p) for p in qs],
            })

        datos = [_punto_to_feature(p)["properties"] | {"coordenadas": _punto_to_feature(p)["geometry"]} for p in qs]
        return public_response(datos, total=len(datos))


class PuntoInteresDetailPublicView(APIView):
    """GET /api/v1/public/puntos-interes/<id>/"""
    permission_classes = [AllowAny]
    throttle_classes = [PublicAPIThrottle]

    def get(self, request, pk):
        try:
            p = Punto_Interes.objects.select_related("id_geometria").get(pk=pk)
        except Punto_Interes.DoesNotExist:
            return Response({"status": "error", "mensaje": "Punto no encontrado"}, status=404)
        return public_response(_punto_to_feature(p))


class SitiosTuristicosPublicView(APIView):
    """GET /api/v1/public/sitios-turisticos/"""
    permission_classes = [AllowAny]
    throttle_classes = [PublicAPIThrottle]

    def get(self, request):
        qs = Sitio_turistico.objects.select_related("id_punto__id_geometria", "id_categoria").all()
        datos = []
        for s in qs:
            feature = _punto_to_feature(s.id_punto)
            feature["properties"]["categoria_sitio"] = s.id_categoria.nombre
            feature["properties"]["reglas_acceso"] = s.reglas_acceso
            datos.append(feature)
        return public_response(datos, total=len(datos))


class RutasPublicView(APIView):
    """GET /api/v1/public/rutas/"""
    permission_classes = [AllowAny]
    throttle_classes = [PublicAPIThrottle]

    def get(self, request):
        qs = Ruta.objects.filter(estado="activa").all()
        datos = [
            {
                "id": r.id_ruta,
                "nombre": r.nombre,
                "descripcion": r.descripcion,
                "duracion_estimada_min": r.duracion_estimada,
                "longitud_km": str(r.longitud_km),
                "dificultad": r.dificultad,
            }
            for r in qs
        ]
        return public_response(datos, total=len(datos))


class OfrendasPublicView(APIView):
    """GET /api/v1/public/ofrendas/"""
    permission_classes = [AllowAny]
    throttle_classes = [PublicAPIThrottle]

    def get(self, request):
        qs = Ofrenda.objects.select_related("id_punto__id_geometria").all()
        datos = []
        for o in qs:
            feature = _punto_to_feature(o.id_punto)
            feature["properties"]["anfitrion"] = o.anfitrion
            datos.append(feature)
        return public_response(datos, total=len(datos))


# ─────────────────────────────────────────────────────────────────────────────
# GRUPO 4 — Reseñas y Satisfacción
# ─────────────────────────────────────────────────────────────────────────────

class ResenasPublicView(APIView):
    """GET /api/v1/public/resenas/ — POST /api/v1/public/resenas/"""
    permission_classes = [AllowAny]
    throttle_classes = [PublicAPIThrottle]

    def get(self, request):
        qs = ResenaGlobal.objects.filter(estado="aprobada").order_by("-fecha_publicacion")
        page = max(1, int(request.query_params.get("page", 1)))
        page_size = min(50, max(1, int(request.query_params.get("page_size", 20))))
        total = qs.count()
        start = (page - 1) * page_size
        datos = [
            {
                "id": r.id_resena,
                "autor": r.autor,
                "calificacion": r.calificacion,
                "comentario": r.comentario,
                "fecha": r.fecha_publicacion.strftime("%Y-%m-%d"),
                "likes": r.likes,
            }
            for r in qs[start: start + page_size]
        ]
        return public_response(datos, total=total, pagina=page, pagina_size=page_size,
                               siguiente=page * page_size < total)

    def post(self, request):
        calificacion = request.data.get("calificacion")
        comentario = request.data.get("comentario", "")
        nombre = request.data.get("nombre_visitante", "Visitante")
        if not calificacion or not (1 <= int(calificacion) <= 5):
            return Response({"status": "error", "mensaje": "calificacion debe ser entre 1 y 5"}, status=400)
        ip = request.META.get("REMOTE_ADDR")
        r = ResenaGlobal.objects.create(
            calificacion=int(calificacion),
            comentario=comentario,
            nombre_visitante=nombre,
            ip_visitante=ip,
            estado="aprobada",
        )
        return Response({"status": "ok", "id": r.id_resena}, status=201)


class ResenasEstadisticasView(APIView):
    """GET /api/v1/public/resenas/estadisticas/"""
    permission_classes = [AllowAny]
    throttle_classes = [PublicAPIThrottle]

    def get(self, request):
        qs = ResenaGlobal.objects.filter(estado="aprobada")
        agg = qs.aggregate(promedio=Avg("calificacion"), total=Count("id_resena"))
        distribucion = {str(i): qs.filter(calificacion=i).count() for i in range(1, 6)}
        datos = {
            "promedio_calificacion": round(agg["promedio"] or 0, 2),
            "total_resenas": agg["total"],
            "distribucion_estrellas": distribucion,
        }
        return public_response(datos)


# ─────────────────────────────────────────────────────────────────────────────
# GRUPO 5 — Encuestas Agregadas
# ─────────────────────────────────────────────────────────────────────────────

class EncuestaResidenteResumenView(APIView):
    """GET /api/v1/public/encuestas/residente/resumen/"""
    permission_classes = [AllowAny]
    throttle_classes = [PublicAPIThrottle]

    def get(self, request):
        qs = EncuestaResidente.objects.all()
        total = qs.count()
        if total == 0:
            return public_response({"total_encuestas": 0})

        agg = qs.aggregate(
            confianza_policia=Avg("confianza_policia"),
            percepcion_inseguridad=Avg("percepcion_inseguridad"),
            tension_festividades=Avg("tension_festividades"),
            acceso_servicios=Avg("acceso_servicios_festividades"),
            perdida_tradicion=Avg("perdida_tradicion"),
            calidad_aire=Avg("calidad_aire"),
            gestion_residuos=Avg("gestion_residuos"),
        )
        generos = dict(qs.values_list("genero").annotate(c=Count("id")))
        datos = {
            "total_encuestas": total,
            "promedios": {k: round(v, 2) if v else None for k, v in agg.items()},
            "distribucion_genero": generos,
        }
        return public_response(datos)


class EncuestaComercioResumenView(APIView):
    """GET /api/v1/public/encuestas/comercio/resumen/"""
    permission_classes = [AllowAny]
    throttle_classes = [PublicAPIThrottle]

    def get(self, request):
        qs = EncuestaComercio.objects.all()
        total = qs.count()
        if total == 0:
            return public_response({"total_encuestas": 0})

        agg = qs.aggregate(
            participacion=Avg("participacion_decisiones"),
            capacitacion=Avg("capacitacion_turistica"),
            integracion=Avg("integracion_turistica"),
        )
        tipos = dict(qs.values_list("tipo_comercio").annotate(c=Count("id")))
        datos = {
            "total_encuestas": total,
            "promedios": {k: round(v, 2) if v else None for k, v in agg.items()},
            "distribucion_tipo_comercio": tipos,
        }
        return public_response(datos)
