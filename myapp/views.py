from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseForbidden, JsonResponse
from django.views.decorators.http import require_http_methods
from .models import RegistroVisita, PersonaVisita, Encuestador, Usuario
from django.contrib.auth.hashers import make_password
from django.db import transaction
from django.contrib.auth import logout
from django.contrib import messages
import subprocess
from django.conf import settings
from datetime import datetime
import os
from .models import Eje, CategoriaIndicador, Indicador, Medicion, EncuestaResidente, EncuestaInstitucional, EncuestaVisitante
from .forms import EncuestaResidenteForm, EncuestaInstitucionalForm, EncuestaVisitanteForm

# Vista principal para el registro de visitas
# - Maneja tanto la creación de nuevos registros como la visualización de registros existentes
# - Requiere autenticación y que el usuario sea encuestador
@login_required
@transaction.atomic  # Garantiza que todas las operaciones de base de datos se completen exitosamente o se reviertan
def registro_visita(request):
    """
    Vista principal para el CRUD de registros de visitas:
    1. Verifica que el usuario autenticado sea un encuestador
    2. Para solicitudes POST: procesa el formulario y crea un nuevo registro
    3. Para solicitudes GET: muestra todos los registros existentes
    
    Funcionamiento:
    - Primero valida los permisos del usuario
    - En POST:
        * Convierte los datos del formulario a los tipos adecuados
        * Crea el registro principal en RegistroVisita
        * Crea los registros asociados en PersonaVisita
        * Maneja errores en la conversión de datos
    - En GET:
        * Recupera todos los registros de visitas
        * Muestra la plantilla con los registros
    """
    
    #1.- Verificar que el usuario es un administrador  
    try:  
        usuario = Usuario.objects.get(nombre_usuario=request.user.username)  
        if usuario.tipo not in ['encuestador', 'admin']:  
            return HttpResponseForbidden("No tienes permiso. Solo los administradores pueden acceder.")  

        if usuario.tipo == 'encuestador':  
            encuestador = Encuestador.objects.get(id_usuario=usuario)  
        else:  # admin  
            encuestador, created = Encuestador.objects.get_or_create(  
                clave_encuestador=f'ADMIN_{usuario.id_usuario}',  
                defaults={'id_usuario': usuario}  
        )  
    except (Usuario.DoesNotExist, Encuestador.DoesNotExist):  
        return HttpResponse('Usuario no encontrado.', status=404)

    # 2. Procesar solicitudes POST (creación de nuevo registro)
    if request.method == 'POST':
        # Función auxiliar para convertir valores a enteros con manejo de errores
        def to_int(value, default=None):
            try:
                return int(value)
            except (TypeError, ValueError):
                return default

        # Obtener y procesar datos del formulario
        es_extranjero = request.POST.get('esExtranjero') == 'si'  # Convertir a booleano
        tamanio_grupo = to_int(request.POST.get('numPersonas'), default=1)
        estancia_dias = to_int(request.POST.get('numDias'), default=1)
        numero_visitas = to_int(request.POST.get('numVisitas'), default=1)
        motivo_visita = request.POST.get('motivo') or None
        tipo_transporte = request.POST.get('transporte') or None

        # Crear el registro principal de visita
        registro = RegistroVisita.objects.create(
            tamanio_grupo=tamanio_grupo,
            es_extranjero=es_extranjero,
            pais_origen=request.POST.get('pais') if es_extranjero else None,  # País solo para extranjeros
            procedencia=request.POST.get('procedencia'),
            tipo_transporte=tipo_transporte,
            motivo_visita=motivo_visita,
            estancia_dias=estancia_dias,
            numero_visitas=numero_visitas,
            id_encuestador=encuestador
        )
        
        # Crear registros para cada persona en el grupo
        personas = []
        for i in range(1, tamanio_grupo + 1):
            edad = to_int(request.POST.get(f'edad{i}'))
            sexo = request.POST.get(f'genero{i}')
            # Validar que los datos de la persona sean correctos
            if edad is not None and sexo in ['Hombre', 'Mujer', 'Otro']:
                personas.append(PersonaVisita(id_registro=registro, edad=edad, sexo=sexo))

        # Crear todas las personas de una vez (optimizado)
        if personas:
            PersonaVisita.objects.bulk_create(personas)
            
        # Redirigir a la lista de registros después de crear
        return redirect('lista_registros')   
    
    # 3. Manejar solicitudes GET (mostrar registros existentes)
    registros = RegistroVisita.objects.all()
    mensaje = request.GET.get('mensaje', '')  # Mensaje opcional para mostrar al usuario
    return render(request, 'myapp/lista_registros.html', {
        'registros': registros, 
        'mensaje': mensaje
    })


def registrar_usuario(request):
    """
    Vista para registrar nuevos usuarios:
    - Valida que todos los campos requeridos estén presentes
    - Crea un nuevo usuario con contraseña hasheada
    - Redirige al login después del registro exitoso
    """
    if request.method == 'POST':
        # Obtener datos del formulario
        nombre = request.POST.get('nombre')
        ap = request.POST.get('ap')
        am = request.POST.get('am')
        nombre_usuario = request.POST.get('nombre_usuario')
        email = request.POST.get('email')
        contrasenia = request.POST.get('contrasenia')
        tipo = request.POST.get('tipo')  

        # Validar campos obligatorios
        if not all([nombre, ap, am, nombre_usuario, email, contrasenia, tipo]):
            return render(request, 'myapp/lista_registros.html', {
                'error': 'Por favor completa todos los campos requeridos'
            })
       
        # Crear usuario con contraseña segura
        usuario = Usuario(
            nombre=nombre,
            ap=ap,
            am=am,
            nombre_usuario=nombre_usuario,
            email=email,
            contrasenia=make_password(contrasenia),  # Hash de contraseña
            tipo=tipo
        )
        usuario.save()
        
        # Redirigir al login
        return redirect('login')  

    # Mostrar formulario de registro
    return render(request, 'myapp/lista_registros.html')


def cerrar_sesion(request):
    """
    Vista para cerrar sesión:
    - Elimina la sesión del usuario
    - Muestra mensaje de confirmación
    - Redirige a la página de login
    """
    logout(request)
    messages.success(request, "Sesión cerrada correctamente.")
    return redirect('login')  

def graficos_indicadores(request):  
    """  
    Vista con menu lateral para graficos e indicadores turisticos
    """  
    return render(request, 'myapp/graficos_indicadores.html')

def vista_inicio(request):
    """
    Vista de inicio de la aplicación
    """
    return render(request, 'myapp/index.html')


def backup_database(request):
    """
    Vista para generar respaldo de la base de datos:
    - Crea un archivo SQL con el volcado de la base de datos
    - Devuelve el archivo como descarga
    - Maneja errores durante el proceso
    """
    try:
        # Obtener configuraciones de la base de datos
        db_name = settings.DATABASES['default']['NAME']
        db_user = settings.DATABASES['default']['USER']
        db_pass = settings.DATABASES['default']['PASSWORD'] or ''
        db_host = settings.DATABASES['default']['HOST'] or 'localhost'
        
        # Crear nombre de archivo único con timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        backup_filename = f"backup_{timestamp}.sql"
        
        # Directorio temporal para guardar el respaldo
        temp_dir = "C:\\Descargas\\respaldo"
        os.makedirs(temp_dir, exist_ok=True)
        backup_path = os.path.join(temp_dir, backup_filename)
        
        # Construir comando para mysqldump
        cmd = [
            'mysqldump',
            f'-h{db_host}',
            f'-u{db_user}',
            f'-p{db_pass}',
            db_name,
            f'--result-file={backup_path}'
        ]
        
        # Ejecutar el comando
        subprocess.run(cmd, check=True)
        
        # Preparar respuesta con el archivo
        with open(backup_path, 'rb') as f:
            response = HttpResponse(f.read(), content_type='application/sql')
            response['Content-Disposition'] = f'attachment; filename={backup_filename}'
        
        # Eliminar archivo temporal
        os.remove(backup_path)
        
        return response
        
    except Exception as e:
        # Manejar errores y devolver mensaje detallado
        return HttpResponse(f"Error al generar el respaldo: {str(e)}", status=500)
    
@login_required  
def eliminar_registro(request, id_registro):  
    """  
    Vista para eliminar un registro individual:  
    - Verifica permisos de usuario  
    - Busca el registro por ID  
    - Intenta eliminarlo  
    - Devuelve mensaje de éxito o error  
    """  
    # Verificar permisos  
    try:  
        usuario = Usuario.objects.get(nombre_usuario=request.user.username)  
        if usuario.tipo not in ['encuestador', 'admin']:  
            return HttpResponseForbidden("No tienes permiso para eliminar registros.")  
    except Usuario.DoesNotExist:  
        return HttpResponse('Usuario no encontrado.', status=404)  
      
    registro = get_object_or_404(RegistroVisita, pk=id_registro)  
      
    try:  
        registro.delete()  
        mensaje = f'Registro {id_registro} eliminado correctamente'  
    except Exception as e:  
        mensaje = f'Error al eliminar registro {id_registro}: {str(e)}'  
      
    # Redirigir con mensaje de estado  
    return redirect(f'/visitas/?mensaje={mensaje}')

def obtener_registro(request, id_registro):
    """
    API para obtener datos de un registro en formato JSON:
    - Usada para precargar el formulario de edición
    - Incluye datos principales y de las personas asociadas
    """
    registro = get_object_or_404(RegistroVisita, pk=id_registro)
    personas = PersonaVisita.objects.filter(id_registro=registro)
    
    # Preparar datos de las personas
    personas_data = []
    for persona in personas:
        personas_data.append({
            'edad': persona.edad,
            'sexo': persona.sexo
        })
    
    # Estructurar respuesta JSON
    data = {
        'id_registro': registro.id_registro,
        'fecha': registro.fecha.strftime('%Y-%m-%d'),
        'tamanio_grupo': registro.tamanio_grupo,
        'es_extranjero': registro.es_extranjero,
        'pais_origen': registro.pais_origen,
        'procedencia': registro.procedencia,
        'tipo_transporte': registro.tipo_transporte,
        'motivo_visita': registro.motivo_visita,
        'estancia_dias': registro.estancia_dias,
        'numero_visitas': registro.numero_visitas,
        'personas': personas_data  # Datos de las personas asociadas
    }
    return JsonResponse(data)


# Vista para editar un registro existente
@login_required
@transaction.atomic
def editar_registro(request, id_registro):
    """
    Vista para editar registros existentes:
    1. Verifica permisos del usuario
    2. Actualiza el registro principal
    3. Actualiza los registros de personas asociadas
    
    Funcionamiento:
    - Elimina las personas existentes y crea nuevas
    - Maneja conversión de tipos de datos
    - Actualiza todos los campos del registro
    """
    try:  
        usuario = Usuario.objects.get(nombre_usuario=request.user.username)  
        if usuario.tipo not in ['encuestador', 'admin']:  
            return HttpResponseForbidden("No tienes permiso para editar registros.")  
        
        if usuario.tipo == 'encuestador':  
            encuestador = Encuestador.objects.get(id_usuario=usuario)  
        else:  # admin  
            encuestador, created = Encuestador.objects.get_or_create(  
                clave_encuestador=f'ADMIN_{usuario.id_usuario}',  
                defaults={'id_usuario': usuario}  
            )  
    except (Usuario.DoesNotExist, Encuestador.DoesNotExist):  
        return HttpResponse('Encuestador no encontrado.', status=404)

    # Obtener registro a editar
    registro = get_object_or_404(RegistroVisita, pk=id_registro)

    if request.method == 'POST':
        # Función para conversión segura a enteros
        def to_int(value, default=None):
            try:
                return int(value)
            except (TypeError, ValueError):
                return default

        # Procesar datos del formulario
        es_extranjero = request.POST.get('esExtranjero') == 'si'
        tamanio_grupo = to_int(request.POST.get('numPersonas'), default=1)
        estancia_dias = to_int(request.POST.get('numDias'), default=1)
        numero_visitas = to_int(request.POST.get('numVisitas'), default=1)
        motivo_visita = request.POST.get('motivo') or None
        tipo_transporte = request.POST.get('transporte') or None

        # Actualizar registro principal
        registro.tamanio_grupo = tamanio_grupo
        registro.es_extranjero = es_extranjero
        registro.pais_origen = request.POST.get('pais') if es_extranjero else None
        registro.procedencia = request.POST.get('procedencia')
        registro.tipo_transporte = tipo_transporte
        registro.motivo_visita = motivo_visita
        registro.estancia_dias = estancia_dias
        registro.numero_visitas = numero_visitas
        registro.save()

        # Eliminar personas existentes y crear nuevas
        PersonaVisita.objects.filter(id_registro=registro).delete()
        personas = []
        for i in range(1, tamanio_grupo + 1):
            edad = to_int(request.POST.get(f'edad{i}'))
            sexo = request.POST.get(f'genero{i}')
            # Validar datos de la persona
            if edad is not None and sexo in ['Hombre', 'Mujer', 'Otro']:
                personas.append(PersonaVisita(id_registro=registro, edad=edad, sexo=sexo))

        # Crear nuevas personas
        if personas:
            PersonaVisita.objects.bulk_create(personas)
            
        # Redirigir a la lista de registros
        return redirect('lista_registros')
    
    # Redirigir si no es POST
    return redirect('lista_registros')


# Vista para eliminación múltiple de registros
@login_required  
def eliminar_seleccionados(request):  
    """  
    Elimina múltiples registros seleccionados:  
    - Recibe IDs como parámetro GET (?ids=1,2,3)  
    - Valida que se hayan seleccionado registros  
    - Maneja errores durante la eliminación  
    """  
    ids_str = request.GET.get('ids', '')  
    if not ids_str:  
        return HttpResponse("No se seleccionaron registros para eliminar", status=400)  
      
    try:    
        usuario = Usuario.objects.get(nombre_usuario=request.user.username)    
        if usuario.tipo not in ['encuestador', 'admin']:    
            return HttpResponseForbidden("No tienes permiso para eliminar registros.")    
    except Usuario.DoesNotExist:    
        return HttpResponse('Usuario no encontrado.', status=404)  
      
    try:  
        # Convertir string de IDs a lista de enteros  
        ids = [int(id) for id in ids_str.split(',')]  
          
        # Eliminar registros  
        RegistroVisita.objects.filter(id_registro__in=ids).delete()  
        mensaje = f'Se eliminaron {len(ids)} registros correctamente'  
    except Exception as e:  
        mensaje = f'Error al eliminar registros: {str(e)}'  
      
    # Redirigir con mensaje de estado  
    return redirect(f'/visitas/?mensaje={mensaje}')

def vista_graficas(request):
    return render(request, 'myapp/charts.html')

@login_required  
def redirigir_por_tipo_usuario(request):  
    """  
    Vista que redirige a los usuarios según su tipo después del login  
    """  
    try:  
        usuario = Usuario.objects.get(nombre_usuario=request.user.username)  
          
        if usuario.tipo == 'encuestador':  
            # Redirigir al formulario de registro para encuestadores  
            return redirect('formulario')  # o la URL específica del formulario  
        
        elif usuario.tipo == 'admin':  
            # Redirigir al CRUD para administradores  
            return redirect('lista_registros')  
        elif usuario.tipo == 'propietario':  
            # Redirigir a una página específica para propietarios  
            return redirect('vista_inicio')  # o donde corresponda  
        else:  
            # Tipo de usuario no reconocido  
            return redirect('login')  
              
    except Usuario.DoesNotExist:  
        return redirect('login')
    


@login_required  
@transaction.atomic  
def formulario(request):  
    """  
    Vista específica para que encuestadores puedan crear registros  
    """  
    try:  
        usuario = Usuario.objects.get(nombre_usuario=request.user.username)  
        if usuario.tipo != 'encuestador':  
            return HttpResponseForbidden("No tienes permiso. Solo los encuestadores pueden acceder.")  
          
        encuestador = Encuestador.objects.get(id_usuario=usuario)  
    except (Usuario.DoesNotExist, Encuestador.DoesNotExist):  
        return HttpResponse('Encuestador no encontrado.', status=404)  
  
    if request.method == 'POST':  
        # Usar el mismo código de procesamiento que registro_visita  
        def to_int(value, default=None):  
            try:  
                return int(value)  
            except (TypeError, ValueError):  
                return default  
  
        es_extranjero = request.POST.get('esExtranjero') == 'si'  
        tamanio_grupo = to_int(request.POST.get('numPersonas'), default=1)  
        estancia_dias = to_int(request.POST.get('numDias'), default=1)  
        numero_visitas = to_int(request.POST.get('numVisitas'), default=1)  
        motivo_visita = request.POST.get('motivo') or None  
        tipo_transporte = request.POST.get('transporte') or None  
  
        # Crear registro  
        registro = RegistroVisita.objects.create(  
            tamanio_grupo=tamanio_grupo,  
            es_extranjero=es_extranjero,  
            pais_origen=request.POST.get('pais') if es_extranjero else None,  
            procedencia=request.POST.get('procedencia'),  
            tipo_transporte=tipo_transporte,  
            motivo_visita=motivo_visita,  
            estancia_dias=estancia_dias,  
            numero_visitas=numero_visitas,  
            id_encuestador=encuestador  
        )  
          
        # Crear personas  
        personas = []  
        for i in range(1, tamanio_grupo + 1):  
            edad = to_int(request.POST.get(f'edad{i}'))  
            sexo = request.POST.get(f'genero{i}')  
            if edad is not None and sexo in ['Hombre', 'Mujer', 'Otro']:  
                personas.append(PersonaVisita(id_registro=registro, edad=edad, sexo=sexo))  
  
        if personas:  
            PersonaVisita.objects.bulk_create(personas)  

        return redirect('formulario')  

    return render(request, 'myapp/formulario.html')



def mapa(request):
    return render(request, "myapp/mapa.html")

#prueba

# views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse, FileResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
# Repository functionality - Models not yet implemented
# from .models import Documento, Categoria

def repositorio(request):
    """Vista principal del repositorio - Pendiente de implementación"""
    # TODO: Implementar modelos Documento y Categoria
    return render(request, 'myapp/repositorio.html', {
        'categorias': [],
        'documentos': [],
        'mensaje': 'Funcionalidad en desarrollo'
    })

@login_required
def dashboard_view(request):
    """
    Vista principal del Dashboard del Observatorio.
    Muestra los indicadores agrupados por Eje y Categoría,
    con datos de sparklines, tendencias y conteos para el dashboard premium.
    """
    import json
    
    ejes = Eje.objects.prefetch_related('categorias__indicadores__mediciones').all()
    
    total_indicadores = 0
    total_categorias = 0
    
    for eje in ejes:
        eje_indicator_count = 0
        for categoria in eje.categorias.all():
            total_categorias += 1
            for indicador in categoria.indicadores.all():
                eje_indicator_count += 1
                # Obtener mediciones ordenadas por período
                mediciones = list(indicador.mediciones.all().order_by('periodo'))
                values = [float(m.valor) for m in mediciones]
                
                # Sparkline data (JSON array of values)
                indicador.sparkline_values = json.dumps(values) if len(values) > 1 else ''
                
                # Trend calculation
                if len(values) >= 2:
                    prev_val = values[-2]
                    last_val = values[-1]
                    if prev_val != 0:
                        change = ((last_val - prev_val) / abs(prev_val)) * 100
                        indicador.trend_percent = f"{abs(change):.1f}"
                        if change > 0.5:
                            indicador.trend_direction = 'up'
                        elif change < -0.5:
                            indicador.trend_direction = 'down'
                        else:
                            indicador.trend_direction = 'stable'
                    else:
                        indicador.trend_direction = 'stable'
                        indicador.trend_percent = '0.0'
                else:
                    indicador.trend_direction = 'stable'
                    indicador.trend_percent = '0.0'
        
        eje.indicator_count = eje_indicator_count
        total_indicadores += eje_indicator_count
    
    return render(request, 'myapp/dashboard.html', {
        'ejes': ejes,
        'total_indicadores': total_indicadores,
        'total_categorias': total_categorias,
    })

@login_required
def category_detail_view(request, category_id):
    """
    Vista detallada para una categoría de indicadores.
    Muestra gráficas comparativas y detalles de todos sus indicadores.
    """
    import json
    from django.shortcuts import get_object_or_404
    
    categoria = get_object_or_404(CategoriaIndicador.objects.prefetch_related('indicadores__mediciones', 'eje'), id=category_id)
    
    # Procesar datos para cada indicador (similar al dashboard)
    indicadores = categoria.indicadores.all()
    for indicador in indicadores:
        mediciones = list(indicador.mediciones.all().order_by('periodo'))
        values = [float(m.valor) for m in mediciones]
        
        indicador.sparkline_values = json.dumps(values) if len(values) > 1 else ''
        
        if len(values) >= 2:
            prev_val = values[-2]
            last_val = values[-1]
            if prev_val != 0:
                change = ((last_val - prev_val) / abs(prev_val)) * 100
                indicador.trend_percent = f"{abs(change):.1f}"
                if change > 0.5:
                    indicador.trend_direction = 'up'
                elif change < -0.5:
                    indicador.trend_direction = 'down'
                else:
                    indicador.trend_direction = 'stable'
            else:
                indicador.trend_direction = 'stable'
                indicador.trend_percent = '0.0'
        else:
            indicador.trend_direction = 'stable'
            indicador.trend_percent = '0.0'
            
    return render(request, 'myapp/category_detail.html', {
        'categoria': categoria,
        'indicadores': indicadores,
        'eje': categoria.eje,
    })


@require_http_methods(["GET"])
def indicator_chart_data(request, indicator_id):
    """
    API endpoint para obtener datos históricos de un indicador.
    Formato optimizado para Chart.js.
    Incluye fuente de datos para visualización.
    """
    try:
        indicador = Indicador.objects.get(id=indicator_id)
        mediciones = indicador.mediciones.all().order_by('periodo')
        
        # Determinar la fuente de datos legible
        source_labels = {
            'manual': 'Datos locales (captura manual)',
            'inegi': 'INEGI — Instituto Nacional de Estadística y Geografía',
            'encuesta': 'Encuesta del Observatorio Territorial',
            'other': 'Fuente externa',
        }
        
        # Determinar la última fecha de actualización
        last_sync_date = indicador.last_sync
        if last_sync_date:
            from django.utils.timezone import localtime
            last_updated_str = localtime(last_sync_date).strftime("%d/%m/%Y %H:%M")
        else:
            last_medicion = mediciones.last()
            if last_medicion and last_medicion.fecha_registro:
                last_updated_str = last_medicion.fecha_registro.strftime("%d/%m/%Y")
            else:
                last_updated_str = "Sin datos"
                
        data = {
            'labels': [m.periodo for m in mediciones],
            'values': [float(m.valor) for m in mediciones],
            'indicator_name': indicador.nombre,
            'unit': indicador.unidad_medida,
            'category': indicador.categoria.nombre,
            'axis': indicador.categoria.eje.nombre,
            'description': indicador.descripcion or '',
            'data_source': indicador.data_source,
            'data_source_label': source_labels.get(indicador.data_source, 'Desconocida'),
            'encuesta_tipo': indicador.encuesta_tipo or '',
            'inegi_id': indicador.inegi_indicator_id or '',
            'last_updated': last_updated_str,
        }
        
        return JsonResponse(data)
        
    except Indicador.DoesNotExist:
        return JsonResponse({'error': 'Indicador no encontrado'}, status=404)



# ============================================
# JSON-stat API Endpoints
# ============================================

@require_http_methods(["GET"])
def indicator_jsonstat_data(request, indicator_id):
    """
    API endpoint que devuelve datos de un indicador en formato JSON-stat 2.0.
    
    Uso:
        GET /api/indicator/5/jsonstat/
    
    Returns:
        JsonResponse con estructura JSON-stat
    """
    from myapp.services.jsonstat_utils import build_simple_timeseries
    from myapp.services.inegi_service import get_inegi_service
    
    try:
        # Obtener el indicador
        indicador = get_object_or_404(Indicador, id=indicator_id)
        
        # Si no tiene ID de INEGI, construir desde BD local
        if not indicador.inegi_indicator_id:
            mediciones = indicador.mediciones.all().order_by('periodo')
            periods = [m.periodo for m in mediciones]
            values = [float(m.valor) for m in mediciones]
            
            jsonstat_data = build_simple_timeseries(
                indicator_name=indicador.nombre,
                periods=periods,
                values=values,
                unit=indicador.unidad_medida,
                source="Local"
            )
        else:
            # Obtener de INEGI en formato JSON-stat
            service = get_inegi_service()
            if not service:
                return JsonResponse(
                    {'error': 'Servicio INEGI no disponible'}, 
                    status=500
                )
            
            jsonstat_data = service.fetch_jsonstat_data(indicador.inegi_indicator_id)
            
            if not jsonstat_data:
                return JsonResponse(
                    {'error': 'No se pudieron obtener datos'}, 
                    status=404
                )
        
        return JsonResponse(jsonstat_data)
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@require_http_methods(["GET"])
def compare_municipalities_view(request):
    """
    API endpoint para comparar un indicador entre múltiples municipios.
    
    Uso:
        GET /api/compare-municipalities/?indicator_id=6207019048&areas=21071,21114,21156
    
    Query params:
        - indicator_id: ID del indicador en INEGI
        - areas: Códigos de municipios separados por coma
    
    Returns:
        JsonResponse con datos JSON-stat multidimensionales [area, time]
    """
    from myapp.services.inegi_service import get_inegi_service
    
    try:
        # Obtener parámetros
        indicator_id = request.GET.get('indicator_id')
        areas_param = request.GET.get('areas', '')
        
        # Validar parámetros
        if not indicator_id or not areas_param:
            return JsonResponse(
                {'error': 'Parámetros indicator_id y areas son requeridos'}, 
                status=400
            )
        
        # Parsear códigos de municipios
        municipality_codes = [code.strip() for code in areas_param.split(',')]
        
        if len(municipality_codes) < 2:
            return JsonResponse(
                {'error': 'Se requieren al menos 2 municipios para comparar'}, 
                status=400
            )
        
        # Obtener servicio INEGI
        service = get_inegi_service()
        if not service:
            return JsonResponse(
                {'error': 'Servicio INEGI no disponible'}, 
                status=500
            )
        
        # Obtener datos comparativos
        jsonstat_data = service.compare_municipalities(
            indicator_id=indicator_id,
            municipality_codes=municipality_codes
        )
        
        if not jsonstat_data:
            return JsonResponse(
                {'error': 'No se pudieron obtener datos comparativos'}, 
                status=404
            )
        
        return JsonResponse(jsonstat_data)
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

# --- PORTAL DEL ENCUESTADOR ---

@login_required
def encuestador_dashboard(request):
    try:  
        usuario = Usuario.objects.get(nombre_usuario=request.user.username)  
        if usuario.tipo not in ['encuestador', 'admin']:  
            return HttpResponseForbidden("No tienes permiso para acceder al portal de encuestadores.")  
    except Usuario.DoesNotExist:
        return HttpResponse('Usuario no encontrado.', status=404)
        
    return render(request, 'myapp/encuestador_dashboard.html')

@login_required
def nueva_encuesta_residente(request):
    try:  
        usuario = Usuario.objects.get(nombre_usuario=request.user.username)  
        if usuario.tipo not in ['encuestador', 'admin']:  
            return HttpResponseForbidden("No tienes permiso.")  
    except Usuario.DoesNotExist:
        return HttpResponse('Usuario no encontrado.', status=404)

    # Intentar obtener el encuestador (puede no existir en la BD legada)
    encuestador = None
    try:
        encuestador = Encuestador.objects.get(id_usuario=usuario)
    except Exception:
        pass

    if request.method == 'POST':
        form = EncuestaResidenteForm(request.POST)
        if form.is_valid():
            encuesta = form.save(commit=False)
            encuesta.encuestador = encuestador
            encuesta.save()
            messages.success(request, 'Encuesta a residente guardada exitosamente.')
            return redirect('encuestador_dashboard')
    else:
        form = EncuestaResidenteForm()

    return render(request, 'myapp/form_residente.html', {'form': form})

@login_required
def nueva_encuesta_institucional(request):
    try:  
        usuario = Usuario.objects.get(nombre_usuario=request.user.username)  
        if usuario.tipo not in ['encuestador', 'admin']:  
            return HttpResponseForbidden("No tienes permiso.")  
    except Usuario.DoesNotExist:
        return HttpResponse('Usuario no encontrado.', status=404)

    # Intentar obtener el encuestador (puede no existir en la BD legada)
    encuestador = None
    try:
        encuestador = Encuestador.objects.get(id_usuario=usuario)
    except Exception:
        pass

    if request.method == 'POST':
        form = EncuestaInstitucionalForm(request.POST)
        if form.is_valid():
            encuesta = form.save(commit=False)
            encuesta.encuestador = encuestador
            encuesta.save()
            messages.success(request, 'Encuesta institucional guardada exitosamente.')
            return redirect('encuestador_dashboard')
    else:
        form = EncuestaInstitucionalForm()

    return render(request, 'myapp/form_institucional.html', {'form': form})

@login_required
def nueva_encuesta_visitante(request):
    try:  
        usuario = Usuario.objects.get(nombre_usuario=request.user.username)  
        if usuario.tipo not in ['encuestador', 'admin']:  
            return HttpResponseForbidden("No tienes permiso.")  
    except Usuario.DoesNotExist:
        return HttpResponse('Usuario no encontrado.', status=404)

    # Intentar obtener el encuestador
    encuestador = None
    try:
        encuestador = Encuestador.objects.get(id_usuario=usuario)
    except Exception:
        pass

    if request.method == 'POST':
        form = EncuestaVisitanteForm(request.POST)
        if form.is_valid():
            encuesta = form.save(commit=False)
            encuesta.encuestador = encuestador
            encuesta.save()
            messages.success(request, 'Encuesta a visitante guardada exitosamente.')
            return redirect('encuestador_dashboard')
    else:
        form = EncuestaVisitanteForm()

    return render(request, 'myapp/form_visitante.html', {'form': form})

# Stub views added to resolve URL resolution errors
def lista_usuarios(request): return HttpResponse("Stub for lista_usuarios")
def crear_usuario(request): return HttpResponse("Stub for crear_usuario")
def editar_usuario(request, id_usuario): return HttpResponse("Stub for editar_usuario")
def eliminar_usuario(request, id_usuario): return HttpResponse("Stub for eliminar_usuario")
def mis_propiedades(request): return HttpResponse("Stub for mis_propiedades")
def editar_mi_propiedad(request, id_punto): return HttpResponse("Stub for editar_mi_propiedad")
def panel_documentos(request): return HttpResponse("Stub for panel_documentos")
def subir_documento(request): return HttpResponse("Stub for subir_documento")
def editar_documento(request, id): return HttpResponse("Stub for editar_documento")
def descargar_documento(request, documento_id): return HttpResponse("Stub for descargar_documento")
def eliminar_documento(request, documento_id): return HttpResponse("Stub for eliminar_documento")
def obtener_documentos_categoria(request, categoria_id): return HttpResponse("Stub for obtener_documentos_categoria")
def subir_desde_url(request): return HttpResponse("Stub for subir_desde_url")
def detalle_archivo(request, archivo_id): return HttpResponse("Stub for detalle_archivo")
def editar_archivo(request, archivo_id): return HttpResponse("Stub for editar_archivo")
def lista_archivos(request): return HttpResponse("Stub for lista_archivos")
def procesar_archivo(request, archivo_id): return HttpResponse("Stub for procesar_archivo")
def actualizar_desde_url(request, archivo_id): return HttpResponse("Stub for actualizar_desde_url")
def eliminar_archivo(request, archivo_id): return HttpResponse("Stub for eliminar_archivo")
def crear_categoria(request): return HttpResponse("Stub for crear_categoria")
def verificar_urls(request): return HttpResponse("Stub for verificar_urls")
def get_categorias_json(request): return HttpResponse("Stub for get_categorias_json")
def lista_puntos(request): return HttpResponse("Stub for lista_puntos")
def detalle_punto(request, punto_id): return HttpResponse("Stub for detalle_punto")
def editar_punto(request, punto_id): return HttpResponse("Stub for editar_punto")
def toggle_visibilidad(request, punto_id): return HttpResponse("Stub for toggle_visibilidad")
def api_resenas_globales(request): return HttpResponse("Stub for api_resenas_globales")
def like_resena(request, resena_id): return HttpResponse("Stub for like_resena")
def reportar_resena(request, resena_id): return HttpResponse("Stub for reportar_resena")
def gestionar_resenas(request): return HttpResponse("Stub for gestionar_resenas")
def cambiar_estado_resena(request, resena_id): return HttpResponse("Stub for cambiar_estado_resena")
def eliminar_resena_admin(request, resena_id): return HttpResponse("Stub for eliminar_resena_admin")
def accion_masiva_resenas(request): return HttpResponse("Stub for accion_masiva_resenas")
def chatbot_api(request): return HttpResponse("Stub for chatbot_api")
