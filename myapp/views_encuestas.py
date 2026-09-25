import json
import csv
import io
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponseForbidden, HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.db.models import Count
from django.utils import timezone
from django.utils.text import slugify
from django.core.files.base import ContentFile

from .models import (
    Usuario, Encuesta, Pregunta, OpcionPregunta,
    RespuestaEncuesta, RespuestaPregunta, Documento, Categoria
)


def check_admin_permission(user):
    """
    Verifica que el usuario tenga rol de administrador (exclusivo para crear,
    editar, eliminar, promover o publicar encuestas en el Observatorio).
    """
    return bool(user.is_authenticated and (
        getattr(user, 'tipo', None) == 'admin' or
        getattr(user, 'is_staff', False) or
        getattr(user, 'is_superuser', False)
    ))


# ─── Gestión de Encuestas (Panel Administrador) ──────────────────────────────

@login_required
def lista_encuestas(request):
    """Lista de encuestas para administración y control multicanal."""
    if not check_admin_permission(request.user):
        return HttpResponseForbidden("Solo los administradores tienen permiso para gestionar encuestas.")
    
    encuestas = Encuesta.objects.all().annotate(
        total_respuestas=Count('respuestas_recibidas', distinct=True)
    ).prefetch_related('documentos_reporte')
    return render(request, 'myapp/encuestas/lista.html', {'encuestas': encuestas})


@login_required
def crear_encuesta(request):
    """Constructor visual de nueva encuesta (Google Forms builder)."""
    if not check_admin_permission(request.user):
        return HttpResponseForbidden("Solo los administradores tienen permiso para crear encuestas.")
    return render(request, 'myapp/encuestas/builder.html', {'survey': None})


@login_required
def editar_encuesta(request, id_encuesta):
    """Edición de encuesta existente en constructor visual."""
    if not check_admin_permission(request.user):
        return HttpResponseForbidden("Solo los administradores tienen permiso para editar encuestas.")
    survey = get_object_or_404(Encuesta, id=id_encuesta)
    return render(request, 'myapp/encuestas/builder.html', {'survey': survey})


@login_required
@transaction.atomic
def guardar_encuesta_api(request):
    """API para guardar o actualizar la estructura y canales de una encuesta."""
    if not check_admin_permission(request.user):
        return JsonResponse({'status': 'error', 'message': 'No autorizado. Se requiere rol de administrador.'}, status=403)
    
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Método no permitido'}, status=405)
    
    try:
        data = json.loads(request.body)
        survey_id = data.get('id')
        titulo = data.get('titulo')
        descripcion = data.get('descripcion', '')
        anonima = data.get('anonima', True)
        activa = data.get('activa', True)
        disponible_web = data.get('disponible_web', True)
        disponible_movil = data.get('disponible_movil', True)
        preguntas_data = data.get('preguntas', [])
        
        if not titulo:
            return JsonResponse({'status': 'error', 'message': 'El título es requerido'}, status=400)
            
        if survey_id:
            survey = get_object_or_404(Encuesta, id=survey_id)
            survey.titulo = titulo
            survey.descripcion = descripcion
            survey.anonima = anonima
            survey.activa = activa
            survey.disponible_web = disponible_web
            survey.disponible_movil = disponible_movil
            survey.save()
        else:
            survey = Encuesta.objects.create(
                titulo=titulo,
                descripcion=descripcion,
                anonima=anonima,
                activa=activa,
                disponible_web=disponible_web,
                disponible_movil=disponible_movil,
                creador=request.user
            )
            
        # Reconstruir las preguntas y opciones
        survey.preguntas.all().delete()
        
        for idx, p_data in enumerate(preguntas_data):
            texto_p = p_data.get('texto')
            tipo_p = p_data.get('tipo_pregunta')
            requerida_p = p_data.get('requerida', False)
            opciones_list = p_data.get('opciones', [])
            
            if not texto_p:
                continue
                
            pregunta = Pregunta.objects.create(
                encuesta=survey,
                texto=texto_p,
                tipo_pregunta=tipo_p,
                requerida=requerida_p,
                orden=idx
            )
            
            if tipo_p in ['OPCION_MULTIPLE', 'CASILLAS', 'DESPLEGABLE']:
                for opt_idx, opt_text in enumerate(opciones_list):
                    if opt_text:
                        OpcionPregunta.objects.create(
                            pregunta=pregunta,
                            texto=opt_text,
                            orden=opt_idx
                        )
                        
        return JsonResponse({'status': 'success', 'survey_id': survey.id})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@login_required
@transaction.atomic
def eliminar_encuesta(request, id_encuesta):
    """Elimina una encuesta y todas sus respuestas asociadas."""
    if not check_admin_permission(request.user):
        return HttpResponseForbidden("Solo los administradores tienen permiso para eliminar encuestas.")
    if request.method == 'POST':
        survey = get_object_or_404(Encuesta, id=id_encuesta)
        survey.delete()
        messages.success(request, f'Encuesta "{survey.titulo}" eliminada correctamente.')
        return redirect('lista_encuestas')
    return HttpResponseForbidden("Método no permitido.")


@login_required
@transaction.atomic
def toggle_encuesta(request, id_encuesta):
    """Alterna el estado general (Activa / Inactiva) de la encuesta."""
    if not check_admin_permission(request.user):
        return JsonResponse({'status': 'error', 'message': 'No autorizado.'}, status=403)
    if request.method == 'POST':
        survey = get_object_or_404(Encuesta, id=id_encuesta)
        survey.activa = not survey.activa
        survey.save()
        return JsonResponse({'status': 'success', 'activa': survey.activa})
    return JsonResponse({'status': 'error', 'message': 'Método no permitido'}, status=405)


@login_required
@transaction.atomic
def toggle_canal_encuesta(request, id_encuesta, canal):
    """
    Alterna individualmente la promoción de un canal:
    - 'web' -> disponible_web
    - 'movil' -> disponible_movil
    """
    if not check_admin_permission(request.user):
        return JsonResponse({'status': 'error', 'message': 'No autorizado.'}, status=403)
    if request.method == 'POST':
        survey = get_object_or_404(Encuesta, id=id_encuesta)
        if canal == 'web':
            survey.disponible_web = not survey.disponible_web
            survey.save()
            return JsonResponse({'status': 'success', 'canal': 'web', 'valor': survey.disponible_web})
        elif canal == 'movil':
            survey.disponible_movil = not survey.disponible_movil
            survey.save()
            return JsonResponse({'status': 'success', 'canal': 'movil', 'valor': survey.disponible_movil})
        return JsonResponse({'status': 'error', 'message': f'Canal "{canal}" no válido'}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Método no permitido'}, status=405)


# ─── Responder Encuesta (Portal Web Público / Nominal) ────────────────────────

def responder_encuesta(request, id_encuesta):
    """Vista web para que la ciudadanía o visitantes respondan la encuesta."""
    survey = get_object_or_404(Encuesta, id=id_encuesta)
    
    if not survey.activa:
        return render(request, 'myapp/encuestas/responder.html', {
            'survey': survey,
            'cerrada': True,
            'mensaje_cierre': 'Esta encuesta se encuentra desactivada actualmente.'
        })
        
    if not survey.disponible_web:
        return render(request, 'myapp/encuestas/responder.html', {
            'survey': survey,
            'cerrada': True,
            'mensaje_cierre': 'Esta encuesta está reservada exclusivamente para levantamiento en campo a través de la App Móvil.'
        })
        
    if request.method == 'POST':
        preguntas = survey.preguntas.all()
        respuestas_a_guardar = []
        errors = {}
        
        for p in preguntas:
            field_name = f'pregunta_{p.id}'
            if p.tipo_pregunta == 'CASILLAS':
                val = request.POST.getlist(field_name)
            else:
                val = request.POST.get(field_name, '').strip()
                
            if p.requerida and (not val or (isinstance(val, list) and len(val) == 0)):
                errors[p.id] = "Esta pregunta es obligatoria."
            
            respuestas_a_guardar.append((p, val))
            
        if errors:
            return render(request, 'myapp/encuestas/responder.html', {
                'survey': survey,
                'errors': errors,
                'respuestas_previas': request.POST
            })
            
        with transaction.atomic():
            usuario_resp = request.user if request.user.is_authenticated else None
            if survey.anonima:
                usuario_resp = None
                
            res_encuesta = RespuestaEncuesta.objects.create(
                encuesta=survey,
                usuario_responde=usuario_resp
            )
            
            for p, val in respuestas_a_guardar:
                if val:
                    if isinstance(val, list):
                        valor_str = json.dumps(val, ensure_ascii=False)
                    else:
                        valor_str = str(val)
                        
                    RespuestaPregunta.objects.create(
                        respuesta_encuesta=res_encuesta,
                        pregunta=p,
                        valor_texto=valor_str
                    )
                    
        return render(request, 'myapp/encuestas/responder.html', {
            'survey': survey,
            'completada': True
        })
        
    return render(request, 'myapp/encuestas/responder.html', {
        'survey': survey,
        'cerrada': False
    })


# ─── Analítica y Estadísticas ────────────────────────────────────────────────

def obtener_stats_encuesta(survey):
    """Función auxiliar que calcula los agregados y frecuencias de cada pregunta."""
    preguntas_stats = []
    for p in survey.preguntas.all():
        respuestas_p = RespuestaPregunta.objects.filter(pregunta=p)
        total_respuestas_p = respuestas_p.count()
        
        stat_data = {
            'id': p.id,
            'texto': p.texto,
            'tipo_pregunta': p.tipo_pregunta,
            'total': total_respuestas_p,
            'respuestas_texto': [],
            'datos_grafico': {'labels': [], 'data': []}
        }
        
        if p.tipo_pregunta in ['TEXTO', 'PARRAFO']:
            stat_data['respuestas_texto'] = [r.valor_texto for r in respuestas_p if r.valor_texto]
        else:
            opciones_definidas = [o.texto for o in p.opciones.all()]
            conteos = {opt: 0 for opt in opciones_definidas}
            
            for r in respuestas_p:
                if not r.valor_texto:
                    continue
                
                if p.tipo_pregunta == 'CASILLAS':
                    try:
                        seleccionadas = json.loads(r.valor_texto)
                        if isinstance(seleccionadas, list):
                            for s in seleccionadas:
                                conteos[s] = conteos.get(s, 0) + 1
                        else:
                            conteos[seleccionadas] = conteos.get(seleccionadas, 0) + 1
                    except Exception:
                        for s in r.valor_texto.split(','):
                            s = s.strip()
                            if s:
                                conteos[s] = conteos.get(s, 0) + 1
                else:
                    conteos[r.valor_texto] = conteos.get(r.valor_texto, 0) + 1
            
            stat_data['datos_grafico'] = {
                'labels': list(conteos.keys()),
                'data': list(conteos.values())
            }
            
        preguntas_stats.append(stat_data)
    return preguntas_stats


@login_required
def ver_respuestas(request, id_encuesta):
    """Panel de analítica visual, gráficos y listado de respuestas individuales."""
    if not check_admin_permission(request.user):
        return HttpResponseForbidden("Solo los administradores pueden consultar los resultados analíticos.")
    
    survey = get_object_or_404(Encuesta, id=id_encuesta)
    total_respuestas = survey.respuestas_recibidas.count()
    preguntas_stats = obtener_stats_encuesta(survey)
    
    respuestas_individuales = survey.respuestas_recibidas.all().order_by('-fecha_envio')
    respuestas_mapeadas = []
    for ri in respuestas_individuales:
        detalle_respuestas = {}
        for dp in ri.detalles.all():
            if dp.pregunta.tipo_pregunta == 'CASILLAS':
                try:
                    vals = json.loads(dp.valor_texto)
                    detalle_respuestas[dp.pregunta.id] = ", ".join(vals)
                except Exception:
                    detalle_respuestas[dp.pregunta.id] = dp.valor_texto
            else:
                detalle_respuestas[dp.pregunta.id] = dp.valor_texto
                
        respuestas_mapeadas.append({
            'id': ri.id,
            'fecha': ri.fecha_envio,
            'usuario': ri.usuario_responde.nombre_usuario if ri.usuario_responde else 'Anónimo',
            'respuestas': detalle_respuestas
        })
        
    documento_publicado = Documento.objects.filter(encuesta=survey).first()

    context = {
        'survey': survey,
        'total_respuestas': total_respuestas,
        'preguntas_stats': preguntas_stats,
        'respuestas_individuales': respuestas_mapeadas,
        'preguntas_lista': [{'id': p.id, 'texto': p.texto} for p in survey.preguntas.all()],
        'documento_publicado': documento_publicado
    }
    return render(request, 'myapp/encuestas/respuestas.html', context)


@login_required
@transaction.atomic
def eliminar_respuesta(request, id_respuesta):
    """Elimina una respuesta individual de encuesta."""
    if not check_admin_permission(request.user):
        return JsonResponse({'status': 'error', 'message': 'No autorizado'}, status=403)
    if request.method == 'POST':
        resp = get_object_or_404(RespuestaEncuesta, id=id_respuesta)
        survey_id = resp.encuesta.id
        resp.delete()
        messages.success(request, 'Respuesta eliminada con éxito.')
        return redirect('ver_respuestas', id_encuesta=survey_id)
    return HttpResponseForbidden("Método no permitido.")


# ─── Generación de Ficha Resumen PDF ──────────────────────────────────────────

def generar_ficha_pdf_encuesta(survey, total_respuestas, preguntas_stats):
    """
    Genera en memoria una Ficha Resumen ejecutiva en formato PDF
    utilizando ReportLab, con el membrete oficial del Observatorio.
    """
    from reportlab.lib.pagesizes import letter
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, KeepTogether
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_CENTER, TA_LEFT

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=16,
        leading=20,
        textColor=colors.HexColor('#2c3e50'),
        alignment=TA_CENTER
    )
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=13,
        textColor=colors.HexColor('#7f8c8d'),
        alignment=TA_CENTER
    )
    section_title = ParagraphStyle(
        'SectionTitle',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=14,
        textColor=colors.HexColor('#3a6073'),
        spaceBefore=10,
        spaceAfter=5
    )
    cell_text = ParagraphStyle(
        'CellText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor('#333333')
    )
    cell_bold = ParagraphStyle(
        'CellBold',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor('#2c3e50')
    )
    footer_text = ParagraphStyle(
        'FooterText',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=8,
        leading=10,
        textColor=colors.HexColor('#95a5a6'),
        alignment=TA_CENTER
    )

    story = []

    # Membrete institucional
    story.append(Paragraph("OBSERVATORIO DE DATOS DE HUAQUECHULA", title_style))
    story.append(Paragraph("FICHA TÉCNICA Y RESUMEN EJECUTIVO DE ENCUESTA", subtitle_style))
    story.append(Spacer(1, 6))
    story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#3a6073'), spaceBefore=2, spaceAfter=10))

    # Metadatos del levantamiento
    fecha_corte = timezone.now().strftime("%d/%m/%Y %H:%M")
    canales = []
    if survey.disponible_web:
        canales.append("Portal Web")
    if survey.disponible_movil:
        canales.append("App Móvil")
    canales_str = ", ".join(canales) if canales else "Inactiva"

    meta_data = [
        [
            Paragraph("<b>Encuesta:</b>", cell_bold), Paragraph(survey.titulo, cell_text),
            Paragraph("<b>Fecha de Generación:</b>", cell_bold), Paragraph(fecha_corte, cell_text)
        ],
        [
            Paragraph("<b>Total Respuestas:</b>", cell_bold), Paragraph(str(total_respuestas), cell_bold),
            Paragraph("<b>Estado General:</b>", cell_bold), Paragraph("Activa" if survey.activa else "Cerrada", cell_text)
        ],
        [
            Paragraph("<b>Modalidad:</b>", cell_bold), Paragraph("Anónima" if survey.anonima else "Con Registro Nominal", cell_text),
            Paragraph("<b>Canales Habilitados:</b>", cell_bold), Paragraph(canales_str, cell_text)
        ],
    ]
    if survey.descripcion:
        meta_data.append([
            Paragraph("<b>Descripción:</b>", cell_bold),
            Paragraph(survey.descripcion, cell_text),
            Paragraph("", cell_text),
            Paragraph("", cell_text)
        ])

    meta_table = Table(meta_data, colWidths=[100, 170, 110, 160])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8f9fa')),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#cbd5e1')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('SPAN', (1, 3), (3, 3)) if survey.descripcion else ('VALIGN', (0, 0), (0, 0), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 10))

    # Resultados y frecuencias por pregunta
    story.append(Paragraph("DESGLOSE DE RESULTADOS POR PREGUNTA", section_title))
    story.append(Spacer(1, 4))

    for idx, stat in enumerate(preguntas_stats, 1):
        q_elements = []
        p_tipo = stat.get('tipo_pregunta', '')
        q_elements.append(Paragraph(f"<b>{idx}. {stat['texto']}</b> <font size=7.5 color='#7f8c8d'>({p_tipo})</font>", cell_bold))
        q_elements.append(Spacer(1, 2))

        if p_tipo in ['TEXTO', 'PARRAFO']:
            respuestas_txt = stat.get('respuestas_texto', [])
            total_txt = len(respuestas_txt)
            ultimas = respuestas_txt[:6]
            q_elements.append(Paragraph(f"<i>Total de respuestas abiertas recibidas: {total_txt}</i>", cell_text))
            if ultimas:
                items_p = [[Paragraph("• " + str(u), cell_text)] for u in ultimas]
                if total_txt > 6:
                    items_p.append([Paragraph(f"<i>... y {total_txt - 6} respuesta(s) adicional(es) registradas en el dataset digital.</i>", footer_text)])
                txt_table = Table(items_p, colWidths=[540])
                txt_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#ffffff')),
                    ('LEFTPADDING', (0, 0), (-1, -1), 8),
                    ('TOPPADDING', (0, 0), (-1, -1), 1.5),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 1.5),
                ]))
                q_elements.append(txt_table)
        else:
            labels = stat.get('datos_grafico', {}).get('labels', [])
            data_counts = stat.get('datos_grafico', {}).get('data', [])
            total_q = sum(data_counts)
            
            table_rows = [
                [Paragraph("<b>Opción</b>", cell_bold), Paragraph("<b>Frecuencia</b>", cell_bold), Paragraph("<b>Porcentaje</b>", cell_bold)]
            ]
            for opt_label, opt_count in zip(labels, data_counts):
                pct = (opt_count / total_q * 100) if total_q > 0 else 0
                table_rows.append([
                    Paragraph(str(opt_label), cell_text),
                    Paragraph(str(opt_count), cell_text),
                    Paragraph(f"{pct:.1f}%", cell_text)
                ])
            table_rows.append([
                Paragraph("<b>Total</b>", cell_bold),
                Paragraph(f"<b>{total_q}</b>", cell_bold),
                Paragraph("<b>100%</b>", cell_bold)
            ])

            q_table = Table(table_rows, colWidths=[340, 100, 100])
            q_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e2e8f0')),
                ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
                ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#f1f5f9')),
                ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#f8fafc')),
                ('TOPPADDING', (0, 0), (-1, -1), 2.5),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 2.5),
            ]))
            q_elements.append(q_table)

        q_elements.append(Spacer(1, 6))
        story.append(KeepTogether(q_elements))

    # Pie de página final
    story.append(Spacer(1, 10))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#cbd5e1'), spaceBefore=5, spaceAfter=6))
    story.append(Paragraph("Observatorio de Datos de Huaquechula • Repositorio Institucional • Generado automáticamente", footer_text))

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()


# ─── Publicación de Reporte en Repositorio ────────────────────────────────────

@login_required
@transaction.atomic
def publicar_reporte_repositorio(request, id_encuesta):
    """
    Genera la Ficha Resumen en PDF y la publica/actualiza como un Documento
    tipo 'reporte' en el Repositorio del Sitio (/repositorio/).
    El Administrador decide si la clasificación es 'publico' o 'privado'.
    """
    if not check_admin_permission(request.user):
        return JsonResponse({'status': 'error', 'message': 'No autorizado. Se requiere rol de administrador.'}, status=403)
        
    survey = get_object_or_404(Encuesta, id=id_encuesta)
    
    if request.method == 'POST':
        clasificacion = request.POST.get('clasificacion', 'publico')
        if clasificacion not in ['publico', 'privado']:
            clasificacion = 'publico'
            
        total_respuestas = survey.respuestas_recibidas.count()
        preguntas_stats = obtener_stats_encuesta(survey)
        
        # Generar Ficha PDF
        pdf_bytes = generar_ficha_pdf_encuesta(survey, total_respuestas, preguntas_stats)
        
        # Obtener o asignar categoría vinculada
        categoria = Categoria.objects.filter(nombre__icontains='Turismo').first() or Categoria.objects.first()
        if not categoria:
            categoria, _ = Categoria.objects.get_or_create(
                nombre="Observatorio y Encuestas",
                defaults={'icono': 'fas fa-poll', 'orden': 1}
            )
        slug_title = slugify(survey.titulo)[:35] or f"encuesta_{survey.id}"
        file_name = f"Ficha_Resumen_Encuesta_{survey.id}_{slug_title}.pdf"
        
        documento = Documento.objects.filter(encuesta=survey).first()
        if not documento:
            documento = Documento(
                titulo=f"Ficha Técnica y Resultados: {survey.titulo}",
                descripcion=f"Ficha ejecutiva y resultados de la encuesta '{survey.titulo}'. Total de respuestas analizadas: {total_respuestas}. Levantamiento multicanal en Huaquechula.",
                tipo='reporte',
                clasificacion=clasificacion,
                es_publico=(clasificacion == 'publico'),
                categoria=categoria,
                clave_admin=request.user,
                encuesta=survey
            )
        else:
            documento.titulo = f"Ficha Técnica y Resultados: {survey.titulo}"
            documento.clasificacion = clasificacion
            documento.es_publico = (clasificacion == 'publico')
            documento.descripcion = f"Ficha ejecutiva actualizada de resultados de la encuesta '{survey.titulo}'. Total de respuestas analizadas: {total_respuestas}. Levantamiento multicanal en Huaquechula."
            if not documento.categoria and categoria:
                documento.categoria = categoria

        documento.archivo.save(file_name, ContentFile(pdf_bytes), save=False)
        documento.save()
        
        if request.headers.get('x-requested-with') == 'XMLHttpRequest' or 'application/json' in request.headers.get('accept', ''):
            return JsonResponse({
                'status': 'success',
                'message': f'Ficha resumen en PDF publicada en el Repositorio como documento {clasificacion}.',
                'documento_id': documento.id,
                'documento_url': documento.archivo.url if documento.archivo else '',
                'clasificacion': clasificacion,
                'es_publico': documento.es_publico
            })
            
        messages.success(request, f'Ficha resumen en PDF publicada con éxito en el Repositorio (Clasificación: {clasificacion}).')
        return redirect('ver_respuestas', id_encuesta=survey.id)
        
    return JsonResponse({'status': 'error', 'message': 'Método no permitido'}, status=405)


# ─── API REST de Datos y Exportación CSV ──────────────────────────────────────

def api_encuesta_datos(request, id_encuesta):
    """
    GET /api/encuestas/<id>/datos/
    Retorna dataset completo en JSON estructurado de la encuesta, sus preguntas y respuestas.
    """
    survey = get_object_or_404(Encuesta, id=id_encuesta)
    
    preguntas_data = []
    for p in survey.preguntas.all():
        preguntas_data.append({
            'id': p.id,
            'texto': p.texto,
            'tipo_pregunta': p.tipo_pregunta,
            'requerida': p.requerida,
            'orden': p.orden,
            'opciones': [o.texto for o in p.opciones.all()]
        })
        
    respuestas_data = []
    for r in survey.respuestas_recibidas.all().order_by('fecha_envio'):
        valores = {}
        for det in r.detalles.all():
            valores[det.pregunta_id] = det.valor_texto
            
        respuestas_data.append({
            'id': r.id,
            'fecha_envio': r.fecha_envio.isoformat(),
            'usuario': r.usuario_responde.nombre_usuario if (r.usuario_responde and not survey.anonima) else 'Anónimo',
            'valores': valores
        })
        
    data = {
        'status': 'success',
        'encuesta': {
            'id': survey.id,
            'titulo': survey.titulo,
            'descripcion': survey.descripcion,
            'fecha_creacion': survey.fecha_creacion.isoformat(),
            'activa': survey.activa,
            'disponible_web': survey.disponible_web,
            'disponible_movil': survey.disponible_movil,
            'anonima': survey.anonima,
            'total_respuestas': len(respuestas_data)
        },
        'preguntas': preguntas_data,
        'respuestas': respuestas_data
    }
    return JsonResponse(data, json_dumps_params={'ensure_ascii': False, 'indent': 2})


def exportar_encuesta_csv(request, id_encuesta):
    """
    GET /api/encuestas/<id>/exportar-csv/
    Genera y descarga un archivo CSV tabular con todas las respuestas recopiladas.
    Incluye BOM UTF-8 para visualización perfecta en Microsoft Excel.
    """
    survey = get_object_or_404(Encuesta, id=id_encuesta)
    preguntas = list(survey.preguntas.all().order_by('orden'))
    
    slug_title = slugify(survey.titulo)[:30] or f"encuesta_{survey.id}"
    filename = f"Encuesta_{survey.id}_{slug_title}.csv"
    response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    writer = csv.writer(response)
    
    # Encabezados
    headers = ['ID_Respuesta', 'Fecha_Envio', 'Usuario']
    for p in preguntas:
        headers.append(f"{p.texto} ({p.tipo_pregunta})")
    writer.writerow(headers)
    
    # Filas de datos
    for r in survey.respuestas_recibidas.all().order_by('fecha_envio'):
        row = [
            r.id,
            r.fecha_envio.strftime('%Y-%m-%d %H:%M:%S'),
            r.usuario_responde.nombre_usuario if (r.usuario_responde and not survey.anonima) else 'Anónimo'
        ]
        detalles_map = {det.pregunta_id: det.valor_texto for det in r.detalles.all()}
        for p in preguntas:
            val = detalles_map.get(p.id, '')
            if p.tipo_pregunta == 'CASILLAS' and val:
                try:
                    parsed = json.loads(val)
                    if isinstance(parsed, list):
                        val = "; ".join(parsed)
                except Exception:
                    pass
            row.append(val)
        writer.writerow(row)
        
    return response
