"""
test_survey_strategy.py — Script de verificación automatizada para la estrategia
de encuestas personalizadas, gobernanza, promoción multicanal, API y PDF en repositorio.
"""
import os
import sys
import django

# Forzar encoding UTF-8 en salida estándar para Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# Setup Django
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.test import RequestFactory
from django.contrib.auth import get_user_model
from myapp.models import (
    Usuario, Encuesta, Pregunta, OpcionPregunta,
    RespuestaEncuesta, RespuestaPregunta, Documento, Categoria
)
from myapp.views_encuestas import (
    check_admin_permission, api_encuesta_datos, exportar_encuesta_csv,
    generar_ficha_pdf_encuesta, obtener_stats_encuesta, publicar_reporte_repositorio,
    toggle_canal_encuesta
)
from myapp.api_views import EncuestaCreadaListView

def run_tests():
    print("=" * 60)
    print("INICIANDO PRUEBAS DE ESTRATEGIA DE ENCUESTAS PERSONALIZADAS")
    print("=" * 60)

    # 1. Verificar usuarios
    admin_user = Usuario.objects.filter(tipo='admin').first()
    if not admin_user:
        admin_user = Usuario.objects.create(
            nombre_usuario='test_admin_survey',
            tipo='admin',
            is_staff=True
        )
    print(f"✓ Usuario Administrador: @{admin_user.nombre_usuario} (tipo={admin_user.tipo})")

    encuestador_user = Usuario.objects.filter(tipo='encuestador').first()
    if not encuestador_user:
        encuestador_user = Usuario.objects.create(
            nombre_usuario='test_enc_survey',
            tipo='encuestador'
        )
    print(f"✓ Usuario Encuestador: @{encuestador_user.nombre_usuario} (tipo={encuestador_user.tipo})")

    # 2. Prueba de Permisos
    assert check_admin_permission(admin_user) is True, "Admin debe tener permiso de administración"
    assert check_admin_permission(encuestador_user) is False, "Encuestador NO debe tener permiso de administración"
    print("✓ Verificación de permisos de gobernanza exclusiva para administrador: EXITOSO")

    # 3. Crear Encuesta de Prueba con preguntas y opciones
    encuesta, created = Encuesta.objects.get_or_create(
        titulo="Encuesta de Prueba Automatizada",
        defaults={
            'descripcion': "Prueba de levantamiento multicanal y generación de ficha ejecutiva",
            'creador': admin_user,
            'activa': True,
            'disponible_web': True,
            'disponible_movil': True,
            'anonima': True
        }
    )
    encuesta.disponible_web = True
    encuesta.disponible_movil = True
    encuesta.save()

    # Preguntas
    p1, _ = Pregunta.objects.get_or_create(
        encuesta=encuesta,
        texto="¿Cómo califica el festival de Huaquechula?",
        defaults={'tipo_pregunta': 'OPCION_MULTIPLE', 'orden': 0}
    )
    OpcionPregunta.objects.get_or_create(pregunta=p1, texto="Excelente", defaults={'orden': 0})
    OpcionPregunta.objects.get_or_create(pregunta=p1, texto="Bueno", defaults={'orden': 1})
    OpcionPregunta.objects.get_or_create(pregunta=p1, texto="Regular", defaults={'orden': 2})

    p2, _ = Pregunta.objects.get_or_create(
        encuesta=encuesta,
        texto="Sugerencias o comentarios adicionales",
        defaults={'tipo_pregunta': 'TEXTO', 'orden': 1}
    )

    # 4. Simular respuestas
    r1 = RespuestaEncuesta.objects.create(encuesta=encuesta)
    RespuestaPregunta.objects.create(respuesta_encuesta=r1, pregunta=p1, valor_texto="Excelente")
    RespuestaPregunta.objects.create(respuesta_encuesta=r1, pregunta=p2, valor_texto="Maravillosa organización")

    r2 = RespuestaEncuesta.objects.create(encuesta=encuesta)
    RespuestaPregunta.objects.create(respuesta_encuesta=r2, pregunta=p1, valor_texto="Bueno")
    RespuestaPregunta.objects.create(respuesta_encuesta=r2, pregunta=p2, valor_texto="Mayor señalética")

    print(f"✓ Encuesta y preguntas creadas con 2 respuestas de prueba: EXITOSO")

    # 5. Probar filtro de canales para Móvil
    rf = RequestFactory()
    req = rf.get('/api/mobile/encuestas-creadas/')
    req.user = encuestador_user

    view = EncuestaCreadaListView()
    view.request = req
    qs = view.get_queryset()
    assert qs.filter(id=encuesta.id).exists(), "La encuesta debe aparecer en móvil cuando disponible_movil=True"

    # Desactivar canal móvil
    encuesta.disponible_movil = False
    encuesta.save()
    qs_sin_movil = view.get_queryset()
    assert not qs_sin_movil.filter(id=encuesta.id).exists(), "La encuesta NO debe aparecer en móvil cuando disponible_movil=False"
    print("✓ Filtro dinámico de canal Móvil en API: EXITOSO")

    # Reactivar móvil
    encuesta.disponible_movil = True
    encuesta.save()

    # 6. Probar API de datos JSON
    req_api = rf.get(f'/api/encuestas/{encuesta.id}/datos/')
    resp_api = api_encuesta_datos(req_api, encuesta.id)
    assert resp_api.status_code == 200
    import json
    data = json.loads(resp_api.content)
    assert data['status'] == 'success'
    assert data['encuesta']['titulo'] == encuesta.titulo
    assert len(data['preguntas']) == 2
    assert len(data['respuestas']) >= 2
    print("✓ Endpoint REST API /api/encuestas/<id>/datos/: EXITOSO")

    # 7. Probar Exportación CSV
    req_csv = rf.get(f'/api/encuestas/{encuesta.id}/exportar-csv/')
    resp_csv = exportar_encuesta_csv(req_csv, encuesta.id)
    assert resp_csv.status_code == 200
    assert 'text/csv' in resp_csv['Content-Type']
    csv_content = resp_csv.content.decode('utf-8-sig')
    assert "¿Cómo califica el festival de Huaquechula?" in csv_content
    print("✓ Exportación tabular CSV con UTF-8 BOM: EXITOSO")

    # 8. Probar Generación de Ficha Resumen PDF
    stats = obtener_stats_encuesta(encuesta)
    pdf_bytes = generar_ficha_pdf_encuesta(encuesta, encuesta.respuestas_recibidas.count(), stats)
    assert len(pdf_bytes) > 1000, "El PDF generado debe contener datos binarios válidos"
    assert pdf_bytes.startswith(b'%PDF'), "El encabezado debe ser un archivo PDF válido"
    print(f"✓ Generación de Ficha Resumen ejecutiva en PDF ({len(pdf_bytes)} bytes): EXITOSO")

    # 9. Probar Publicación en Repositorio (Documento)
    req_pub = rf.post(f'/encuestas/{encuesta.id}/publicar-repositorio/', {'clasificacion': 'publico'}, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
    req_pub.user = admin_user
    resp_pub = publicar_reporte_repositorio(req_pub, encuesta.id)
    assert resp_pub.status_code == 200
    pub_data = json.loads(resp_pub.content)
    assert pub_data['status'] == 'success'

    doc = Documento.objects.filter(encuesta=encuesta).first()
    assert doc is not None, "El Documento debe haberse creado en la base de datos"
    assert doc.tipo == 'reporte'
    assert doc.es_publico is True
    assert doc.archivo is not None
    print(f"✓ Publicación en el Repositorio (Documento ID {doc.id}, Archivo: {doc.archivo.name}): EXITOSO")

    # Probar actualización con clasificación Privado
    req_pub_priv = rf.post(f'/encuestas/{encuesta.id}/publicar-repositorio/', {'clasificacion': 'privado'}, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
    req_pub_priv.user = admin_user
    resp_pub_priv = publicar_reporte_repositorio(req_pub_priv, encuesta.id)
    assert resp_pub_priv.status_code == 200
    doc.refresh_from_db()
    assert doc.clasificacion == 'privado'
    assert doc.es_publico is False
    print("✓ Actualización a Clasificación 'Privado' en Repositorio: EXITOSO")

    print("=" * 60)
    print("TODAS LAS PRUEBAS PASARON EXITOSAMENTE (100% OK)")
    print("=" * 60)

if __name__ == '__main__':
    run_tests()
