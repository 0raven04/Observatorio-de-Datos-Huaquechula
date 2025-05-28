from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from .models import RegistroVisita, PersonaVisita, Encuestador, Usuario
from django.http import HttpResponseForbidden
from django.contrib.auth.hashers import make_password
from django.db import transaction
from .forms import RegistroVisitaForm, PersonaFormSet
from django.contrib.auth import logout
from django.contrib import messages
@login_required
@transaction.atomic
def registro_visita(request):
    # 1. comprueba que el usuario sea encuestador
    try:
        usuario = Usuario.objects.get(nombre_usuario=request.user.username)
        if usuario.tipo != 'encuestador':
            return HttpResponseForbidden("No tienes permiso.")
        encuestador = Encuestador.objects.get(id_usuario=usuario)
    except (Usuario.DoesNotExist, Encuestador.DoesNotExist):
        return HttpResponse('Encuestador no encontrado.', status=404)

    if request.method == 'POST':
        # ---------- lógica de guardado ----------
        def to_int(value, default=None):
            try:
                return int(value)
            except (TypeError, ValueError):
                if not personas:
                    return render(request, 'myapp/formulario.html', {'error': 'Faltan datos válidos de personas.'})
                return default

        es_extranjero = request.POST.get('esExtranjero') == 'si'
        tamanio_grupo  = to_int(request.POST.get('numPersonas'), default=1)
        estancia_dias  = to_int(request.POST.get('numDias'),default=1)
        numero_visitas = to_int(request.POST.get('numVisitas'), default=1)

        motivo_visita   = request.POST.get('motivo')      or None
        tipo_transporte = request.POST.get('transporte')  or None

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
        # personas
        personas = []
        for i in range(1, tamanio_grupo + 1):
            edad = to_int(request.POST.get(f'edad{i}'))
            sexo = request.POST.get(f'genero{i}')
            if edad is not None and sexo in ['Hombre', 'Mujer', 'Otro']:
                personas.append(PersonaVisita(id_registro=registro, edad=edad, sexo=sexo))

        if personas:
            PersonaVisita.objects.bulk_create(personas)

        return redirect('registro')      # ← responde al POST   

    return render(request, 'myapp/formulario.html')  






def registrar_usuario(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        ap = request.POST.get('ap')
        am = request.POST.get('am')
        nombre_usuario = request.POST.get('nombre_usuario')
        email = request.POST.get('email')
        contrasenia = request.POST.get('contrasenia')
        tipo = request.POST.get('tipo')  

        if not all([nombre, ap, am, nombre_usuario, email, contrasenia, tipo]):
            return render(request, 'registro.html', {'error': 'Completa todos los campos'})
       
        
        # Crear usuario con contraseña hasheada
        usuario = Usuario(
            nombre=nombre,
            ap=ap,
            am=am,
            nombre_usuario=nombre_usuario,
            email=email,
            contrasenia=make_password(contrasenia),
            tipo=tipo
        )
        usuario.save()
        return redirect('login')  

    return render(request, 'registro.html')

def cerrar_sesion(request):
    logout(request)
    messages.success(request, "Sesión cerrada correctamente.")
    return redirect('login')  


def vista_inicio(request):
    return render(request, 'myapp/index.html')



#Respaldo de base de datos formulario formato .sql
import subprocess
from django.http import HttpResponse
from django.conf import settings
from datetime import datetime
import os

def backup_database(request):
    try:
        db_name = settings.DATABASES['default']['NAME']
        db_user = settings.DATABASES['default']['USER']
        db_pass = settings.DATABASES['default']['PASSWORD'] or ''
        db_host = settings.DATABASES['default']['HOST'] or 'localhost'
        
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        backup_filename = f"backup_{timestamp}.sql"
        
        # Usar una ruta temporal sin espacios
        temp_dir = "C:\\Descargas\\respaldo"
        os.makedirs(temp_dir, exist_ok=True)
        backup_path = os.path.join(temp_dir, backup_filename)
        
        # Construir el comando de manera más segura
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
        
        # Leer el archivo y enviarlo como respuesta
        with open(backup_path, 'rb') as f:
            response = HttpResponse(f.read(), content_type='application/sql')
            response['Content-Disposition'] = f'attachment; filename={backup_filename}'
        
        # Eliminar el archivo temporal
        os.remove(backup_path)
        
        return response
        
    except Exception as e:
        return HttpResponse(f"Error detallado: {str(e)}", status=500)