import json
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponseForbidden, HttpResponse
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Count
from django.utils import timezone
from .models import Usuario, Encuesta, Pregunta, OpcionPregunta, RespuestaEncuesta, RespuestaPregunta

def check_permission(user):
    return user.is_authenticated and user.tipo in ['admin', 'encuestador']

@login_required
def lista_encuestas(request):
    if not check_permission(request.user):
        return HttpResponseForbidden("No tienes permiso para acceder a esta sección.")
    
    encuestas = Encuesta.objects.all().annotate(
        total_respuestas=Count('respuestas_recibidas', distinct=True)
    )
    return render(request, 'myapp/encuestas/lista.html', {'encuestas': encuestas})

@login_required
def crear_encuesta(request):
    if not check_permission(request.user):
        return HttpResponseForbidden("No tienes permiso para crear encuestas.")
    return render(request, 'myapp/encuestas/builder.html', {'survey': None})

@login_required
def editar_encuesta(request, id_encuesta):
    if not check_permission(request.user):
        return HttpResponseForbidden("No tienes permiso para editar encuestas.")
    survey = get_object_or_404(Encuesta, id=id_encuesta)
    return render(request, 'myapp/encuestas/builder.html', {'survey': survey})

@login_required
@transaction.atomic
def guardar_encuesta_api(request):
    if not check_permission(request.user):
        return JsonResponse({'status': 'error', 'message': 'No autorizado'}, status=403)
    
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Método no permitido'}, status=405)
    
    try:
        data = json.loads(request.body)
        survey_id = data.get('id')
        titulo = data.get('titulo')
        descripcion = data.get('descripcion', '')
        anonima = data.get('anonima', True)
        activa = data.get('activa', True)
        preguntas_data = data.get('preguntas', [])
        
        if not titulo:
            return JsonResponse({'status': 'error', 'message': 'El título es requerido'}, status=400)
            
        if survey_id:
            # Editar encuesta existente
            survey = get_object_or_404(Encuesta, id=survey_id)
            survey.titulo = titulo
            survey.descripcion = descripcion
            survey.anonima = anonima
            survey.activa = activa
            survey.save()
        else:
            # Crear nueva encuesta
            survey = Encuesta.objects.create(
                titulo=titulo,
                descripcion=descripcion,
                anonima=anonima,
                activa=activa,
                creador=request.user
            )
            
        # Reconstruir las preguntas
        # Para hacer el builder extremadamente robusto, borramos las preguntas y opciones previas y recreamos.
        # (El frontend avisará al usuario de que editar una encuesta con respuestas borrará la estructura previa).
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
            
            # Crear opciones si aplica
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
    if not check_permission(request.user):
        return HttpResponseForbidden("No tienes permiso.")
    if request.method == 'POST':
        survey = get_object_or_404(Encuesta, id=id_encuesta)
        survey.delete()
        return redirect('lista_encuestas')
    return HttpResponseForbidden("Método no permitido.")

@login_required
@transaction.atomic
def toggle_encuesta(request, id_encuesta):
    if not check_permission(request.user):
        return JsonResponse({'status': 'error', 'message': 'No autorizado'}, status=403)
    if request.method == 'POST':
        survey = get_object_or_404(Encuesta, id=id_encuesta)
        survey.activa = not survey.activa
        survey.save()
        return JsonResponse({'status': 'success', 'activa': survey.activa})
    return JsonResponse({'status': 'error', 'message': 'Método no permitido'}, status=405)

def responder_encuesta(request, id_encuesta):
    survey = get_object_or_404(Encuesta, id=id_encuesta)
    
    if not survey.activa:
        return render(request, 'myapp/encuestas/responder.html', {
            'survey': survey,
            'cerrada': True
        })
        
    if request.method == 'POST':
        # Validar respuestas
        preguntas = survey.preguntas.all()
        respuestas_a_guardar = []
        errors = {}
        
        for p in preguntas:
            field_name = f'pregunta_{p.id}'
            
            if p.tipo_pregunta == 'CASILLAS':
                val = request.POST.getlist(field_name)
            else:
                val = request.POST.get(field_name, '').strip()
                
            # Validar requeridos
            if p.requerida:
                if not val:
                    errors[p.id] = "Esta pregunta es obligatoria."
            
            respuestas_a_guardar.append((p, val))
            
        if errors:
            return render(request, 'myapp/encuestas/responder.html', {
                'survey': survey,
                'errors': errors,
                'respuestas_previas': request.POST
            })
            
        # Guardar en BD
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
                        valor_str = json.dumps(val)
                    else:
                        valor_str = val
                        
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

@login_required
def ver_respuestas(request, id_encuesta):
    if not check_permission(request.user):
        return HttpResponseForbidden("No tienes permiso para ver respuestas.")
    
    survey = get_object_or_404(Encuesta, id=id_encuesta)
    total_respuestas = survey.respuestas_recibidas.count()
    
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
                                if s in conteos:
                                    conteos[s] += 1
                                else:
                                    conteos[s] = conteos.get(s, 0) + 1
                        else:
                            if seleccionadas in conteos:
                                conteos[seleccionadas] += 1
                    except json.JSONDecodeError:
                        for s in r.valor_texto.split(','):
                            s = s.strip()
                            if s in conteos:
                                conteos[s] += 1
                else:
                    if r.valor_texto in conteos:
                        conteos[r.valor_texto] += 1
                    else:
                        conteos[r.valor_texto] = conteos.get(r.valor_texto, 0) + 1
            
            stat_data['datos_grafico'] = {
                'labels': list(conteos.keys()),
                'data': list(conteos.values())
            }
            
        preguntas_stats.append(stat_data)
        
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
        
    context = {
        'survey': survey,
        'total_respuestas': total_respuestas,
        'preguntas_stats': preguntas_stats,
        'respuestas_individuales': respuestas_mapeadas,
        'preguntas_lista': [{'id': p.id, 'texto': p.texto} for p in survey.preguntas.all()]
    }
    
    return render(request, 'myapp/encuestas/respuestas.html', context)

@login_required
@transaction.atomic
def eliminar_respuesta(request, id_respuesta):
    if not check_permission(request.user):
        return JsonResponse({'status': 'error', 'message': 'No autorizado'}, status=403)
    if request.method == 'POST':
        resp = get_object_or_404(RespuestaEncuesta, id=id_respuesta)
        survey_id = resp.encuesta.id
        resp.delete()
        return redirect('ver_respuestas', id_encuesta=survey_id)
    return HttpResponseForbidden("Método no permitido.")
