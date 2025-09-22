from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseForbidden, JsonResponse
from .models import RegistroVisita, PersonaVisita, Encuestador, Usuario
from django.contrib.auth.hashers import make_password
from django.db import transaction
from django.contrib.auth import logout
from django.contrib import messages
import subprocess
from django.conf import settings
from datetime import datetime
import os
from .models import Lugar

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