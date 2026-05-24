from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseForbidden, JsonResponse, FileResponse
from django.apps import apps
from myapp.models import (
    ArchivoKMZ, GeometriaEspacial, Punto_Interes, Categoria_Sitio, Galeria_Multimedia,
    Servicio, Ofrenda, Documento, Administrador, Sitio_turistico, Usuario, Encuestador,
    RegistroVisita, ResenaGlobal, Propietario
)
from django.utils import timezone
from django.utils import timezone as tz
from datetime import timedelta
from django.http import HttpResponse, HttpResponseForbidden, JsonResponse
from django.views.decorators.http import require_http_methods
from .models import RegistroVisita, Encuestador, Usuario
from django.contrib.auth.hashers import make_password
from django.db import IntegrityError, transaction
from django.contrib.auth import logout
from django.contrib import messages
import subprocess
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from datetime import datetime
import os
import sys
from django.shortcuts import render
import urllib.parse
import urllib.error
import secrets
import string
import hashlib

from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import get_user_model
from django.views.decorators.http import require_POST
from .kml_processor import KMLProcessor
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.db.models import Sum, Count, Q
from django.core.files.storage import FileSystemStorage
import datetime  # Este es el módulo
from datetime import datetime as dt  # Este es la clase
from django.http import HttpResponseNotFound
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.core.paginator import Paginator
from django.contrib.auth.models import User 
import urllib.request
import hashlib
from urllib.parse import urlparse
import mimetypes
from myapp.models import Categoria_Sitio
from .models import Eje, CategoriaIndicador, Indicador, Medicion, EncuestaResidente, EncuestaComercio
from .forms import EncuestaResidenteForm, EncuestaComercioForm
from django.views.decorators.http import require_POST, require_http_methods
from django.contrib.auth.hashers import make_password
from django.db import transaction
from django.contrib import messages
from .models import Usuario, RegistroVisita, Encuestador, Documento, Categoria, Lugar
from django.db.models import Sum, Q
import subprocess
import os
from datetime import datetime



from django.views.decorators.csrf import csrf_exempt
import requests

def registrar_usuario(request):
    """
    Vista para registrar nuevos usuarios:
    - Valida que todos los campos requeridos estén presentesr
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
            return render(request, 'myapp/mod_db/crud_kml.html', {
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


def mask_email(email):
    if not email or '@' not in email:
        return email
    local, domain = email.split('@', 1)
    if len(local) <= 2:
        masked = '*' * len(local)
    else:
        masked = f"{local[0]}{'*' * (len(local) - 2)}{local[-1]}"
    return f"{masked}@{domain}"


def get_request_data(request):
    content_type = request.content_type or ''
    if content_type.startswith('application/json'):
        try:
            return json.loads(request.body.decode('utf-8'))
        except ValueError:
            return {}
    return request.POST


def authenticate_username_or_email(request, identifier, password):
    identifier = (identifier or '').strip()
    if '@' in identifier:
        try:
            usuario = Usuario.objects.get(email__iexact=identifier)
            identifier = usuario.nombre_usuario
        except Usuario.DoesNotExist:
            return None
    return authenticate(request, username=identifier, password=password)


def send_two_factor_email(user, code):
    subject = 'Código de verificación - Observatorio de Datos de Huaquechula'
    context = {
        'user': user,
        'code': code,
        'system_name': 'Observatorio de Datos de Huaquechula',
        'expires_minutes': 5,
    }
    text_content = (
        f"Hola {user.nombre},\n\n"
        f"Tu código de verificación es: {code}\n"
        f"Este código expirará en {context['expires_minutes']} minutos.\n\n"
        "Si no pediste este código, ignora este mensaje.\n"
        "Gracias por usar el Observatorio de Datos de Huaquechula."
    )
    html_content = render_to_string('registration/2fa_email.html', context)
    message = EmailMultiAlternatives(
        subject,
        text_content,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
    )
    message.attach_alternative(html_content, 'text/html')
    message.send(fail_silently=False)
    if settings.EMAIL_BACKEND == 'django.core.mail.backends.console.EmailBackend':
        print(f"[2FA DEBUG] Código de verificación para {user.email}: {code}")


def login_with_2fa(request):
    next_url = request.GET.get('next') or request.POST.get('next') or settings.LOGIN_REDIRECT_URL
    if request.method == 'GET':
        return render(request, 'registration/login.html', {'next': next_url})

    data = get_request_data(request)
    username_or_email = data.get('username', '').strip()
    password = data.get('password', '')
    is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest' or (request.content_type or '').startswith('application/json')

    if not username_or_email or not password:
        error_message = 'Por favor ingresa usuario/correo y contraseña.'
        if is_ajax:
            return JsonResponse({
                'status': 'missing_credentials',
                'message': error_message
            }, status=400)
        return render(request, 'registration/login.html', {'next': next_url, 'error_message': error_message})

    user = authenticate_username_or_email(request, username_or_email, password)
    if user is None:
        error_message = 'Usuario o contraseña incorrectos.'
        if is_ajax:
            return JsonResponse({
                'status': 'invalid_credentials',
                'message': error_message
            }, status=401)
        return render(request, 'registration/login.html', {'next': next_url, 'error_message': error_message})

    if not user.is_active:
        error_message = 'La cuenta no está activa. Contacta al administrador.'
        if is_ajax:
            return JsonResponse({
                'status': 'inactive_user',
                'message': error_message
            }, status=403)
        return render(request, 'registration/login.html', {'next': next_url, 'error_message': error_message})

    from .models import TwoFactorCode
    code_obj, code = TwoFactorCode.create_for_user(
        user,
        ip_address=request.META.get('REMOTE_ADDR'),
        user_agent=request.META.get('HTTP_USER_AGENT', '')[:255],
    )

    try:
        send_two_factor_email(user, code)
    except Exception as exc:
        error_message = 'No se pudo enviar el correo de verificación. Revisa la configuración SMTP.'
        if is_ajax:
            return JsonResponse({
                'status': 'email_failed',
                'message': error_message,
                'detail': str(exc),
            }, status=500)
        return render(request, 'registration/login.html', {
            'next': next_url,
            'error_message': error_message,
        })

    request.session['pre_2fa_user_id'] = user.pk
    request.session['pre_2fa_next'] = next_url
    request.session['last_2fa_resend'] = timezone.now().timestamp()

    result = {
        'email': mask_email(user.email),
        'expiry_seconds': 300,
        'next': next_url,
    }
    if settings.EMAIL_BACKEND == 'django.core.mail.backends.console.EmailBackend':
        result['email_backend'] = 'console'

    if is_ajax:
        return JsonResponse({'status': 'challenge', **result})

    return render(request, 'registration/login.html', {
        'next': next_url,
        'initial_2fa': json.dumps(result),
    })


@require_POST
def verify_2fa_code(request):
    data = get_request_data(request)
    code = (data.get('code') or '').strip()
    user_id = request.session.get('pre_2fa_user_id')

    if not user_id:
        return JsonResponse({
            'status': 'session_expired',
            'message': 'La sesión de autenticación expiró. Vuelve a iniciar sesión.'
        }, status=401)

    try:
        user = Usuario.objects.get(pk=user_id)
    except Usuario.DoesNotExist:
        return JsonResponse({
            'status': 'invalid_session',
            'message': 'No se encontró el usuario. Inicia sesión nuevamente.'
        }, status=404)

    from .models import TwoFactorCode
    code_obj = TwoFactorCode.objects.filter(user=user, used=False).order_by('-created_at').first()
    if code_obj is None or code_obj.is_expired():
        return JsonResponse({
            'status': 'expired',
            'message': 'El código expiró. Reenvía uno nuevo.',
        }, status=400)

    if not code_obj.verify_code(code):
        code_obj.attempts += 1
        code_obj.save(update_fields=['attempts'])
        remaining = max(0, 5 - code_obj.attempts)
        if remaining <= 0:
            code_obj.mark_as_used()
            return JsonResponse({
                'status': 'blocked',
                'message': 'Has excedido el número de intentos. Se generará un nuevo código.',
            }, status=403)
        return JsonResponse({
            'status': 'invalid_code',
            'message': 'Código incorrecto. Intenta de nuevo.',
            'remaining_attempts': remaining,
        }, status=400)

    code_obj.mark_as_used()
    login(request, user)
    next_url = request.session.pop('pre_2fa_next', settings.LOGIN_REDIRECT_URL)
    request.session.pop('pre_2fa_user_id', None)
    request.session.pop('last_2fa_resend', None)

    return JsonResponse({
        'status': 'ok',
        'redirect_url': next_url,
    })


@require_POST
def resend_2fa_code(request):
    user_id = request.session.get('pre_2fa_user_id')
    if not user_id:
        return JsonResponse({
            'status': 'session_expired',
            'message': 'La sesión de autenticación expiró. Vuelve a iniciar sesión.'
        }, status=401)

    last_resend = request.session.get('last_2fa_resend')
    now_ts = timezone.now().timestamp()
    if last_resend and now_ts - float(last_resend) < 30:
        return JsonResponse({
            'status': 'too_early',
            'message': 'Espera unos segundos antes de reenviar el código.',
            'retry_seconds': int(30 - (now_ts - float(last_resend)))
        }, status=429)

    try:
        user = Usuario.objects.get(pk=user_id)
    except Usuario.DoesNotExist:
        return JsonResponse({
            'status': 'invalid_session',
            'message': 'No se encontró el usuario. Inicia sesión nuevamente.'
        }, status=404)

    from .models import TwoFactorCode
    code_obj, code = TwoFactorCode.create_for_user(
        user,
        ip_address=request.META.get('REMOTE_ADDR'),
        user_agent=request.META.get('HTTP_USER_AGENT', '')[:255],
    )

    try:
        send_two_factor_email(user, code)
    except Exception as exc:
        return JsonResponse({
            'status': 'email_failed',
            'message': 'No se pudo enviar el correo de verificación. Revisa la configuración SMTP.',
            'detail': str(exc),
        }, status=500)

    request.session['last_2fa_resend'] = now_ts
    return JsonResponse({
        'status': 'resent',
        'expiry_seconds': 300,
        'email': mask_email(user.email),
    })


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
        timestamp = dt.now().strftime("%Y-%m-%d_%H-%M-%S")
        backup_filename = f"backup_{timestamp}.sql"
        
        # Directorio temporal para guardar el respaldo (usando /tmp para Linux/Docker)
        temp_dir = "/tmp/respaldo"
        os.makedirs(temp_dir, exist_ok=True)
        backup_path = os.path.join(temp_dir, backup_filename)
        
        # Construir comando para mysqldump
        cmd = [
            'mysqldump',
            f'-h{db_host}',
            f'-u{db_user}',
            f'-p{db_pass}',
            '--skip-ssl',
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
@transaction.atomic
def registro_visita(request):
    """
    Vista principal para el CRUD de registros de visitas
    """
    
    # 1. Verificar que el usuario tiene permisos
    try:  
        usuario = Usuario.objects.get(nombre_usuario=request.user.nombre_usuario)  
        if usuario.tipo not in ['encuestador', 'admin']:  
            return HttpResponseForbidden("No tienes permiso. Solo encuestadores y administradores pueden acceder.")  

        if usuario.tipo == 'encuestador':  
            encuestador = Encuestador.objects.get(id_usuario=usuario)  
        else:  # admin  
            # Crear encuestador para administrador si no existe
            encuestador, created = Encuestador.objects.get_or_create(
                id_usuario=usuario,
                defaults={
                    'clave_encuestador': usuario.id_usuario
                }
            )
    except Usuario.DoesNotExist:
        return HttpResponse('Usuario no encontrado.', status=404)
    except Encuestador.DoesNotExist:
        return HttpResponse('Encuestador no encontrado.', status=404)

    # 2. Procesar solicitudes POST (creación de nuevo registro)
    if request.method == 'POST':
        # Función auxiliar para convertir valores a enteros
        def to_int(value, default=None):
            try:
                return int(value)
            except (TypeError, ValueError):
                return default

        # Obtener y procesar datos del formulario
        es_extranjero = request.POST.get('es_extranjero') == '1'
        estancia_dias = to_int(request.POST.get('estancia_dias'), default=1)
        visitas_previas = to_int(request.POST.get('visitas_previas'), default=1)  # CAMPO AGREGADO
        motivo_visita = request.POST.get('motivo_visita', 'turismo')
        tipo_transporte = request.POST.get('tipo_transporte', 'automovil')
        procedencia = request.POST.get('procedencia', '')
        pais_origen = request.POST.get('pais_origen') if es_extranjero else None
        
        # Obtener valores de la tabla de edades y géneros
        mujeres_0_15 = to_int(request.POST.get('mujeres_0_15'), 0)
        mujeres_16_30 = to_int(request.POST.get('mujeres_16_30'), 0)
        mujeres_31_45 = to_int(request.POST.get('mujeres_31_45'), 0)
        mujeres_46_60 = to_int(request.POST.get('mujeres_46_60'), 0)
        mujeres_61_75 = to_int(request.POST.get('mujeres_61_75'), 0)
        mujeres_76_mas = to_int(request.POST.get('mujeres_76_mas'), 0)
        
        hombres_0_15 = to_int(request.POST.get('hombres_0_15'), 0)
        hombres_16_30 = to_int(request.POST.get('hombres_16_30'), 0)
        hombres_31_45 = to_int(request.POST.get('hombres_31_45'), 0)
        hombres_46_60 = to_int(request.POST.get('hombres_46_60'), 0)
        hombres_61_75 = to_int(request.POST.get('hombres_61_75'), 0)
        hombres_76_mas = to_int(request.POST.get('hombres_76_mas'), 0)
        
        # Calcular el total de personas
        total_mujeres = sum([
            mujeres_0_15, mujeres_16_30, mujeres_31_45, 
            mujeres_46_60, mujeres_61_75, mujeres_76_mas
        ])
        
        total_hombres = sum([
            hombres_0_15, hombres_16_30, hombres_31_45,
            hombres_46_60, hombres_61_75, hombres_76_mas
        ])
        
        total_personas = total_mujeres + total_hombres
        
        # Validar que haya al menos una persona
        if total_personas == 0:
            messages.error(request, 'Debe ingresar al menos una persona para registrar.')
            registros = RegistroVisita.objects.all()
            return render(request, 'myapp/lista_registros.html', {
                'registros': registros
            })
        
        try:
            # Crear el registro principal de visita
            registro = RegistroVisita.objects.create(
                estancia_dias=estancia_dias,
                visitas_previas=visitas_previas,  # CAMPO AGREGADO
                motivo_visita=motivo_visita,
                tipo_transporte=tipo_transporte,
                procedencia=procedencia,
                pais_origen=pais_origen,
                es_extranjero=es_extranjero,
                clave_encuestador=encuestador,
                # Campos de distribución por edad y género
                mujeres_0_15=mujeres_0_15,
                mujeres_16_30=mujeres_16_30,
                mujeres_31_45=mujeres_31_45,
                mujeres_46_60=mujeres_46_60,
                mujeres_61_75=mujeres_61_75,
                mujeres_76_mas=mujeres_76_mas,
                hombres_0_15=hombres_0_15,
                hombres_16_30=hombres_16_30,
                hombres_31_45=hombres_31_45,
                hombres_46_60=hombres_46_60,
                hombres_61_75=hombres_61_75,
                hombres_76_mas=hombres_76_mas
            )
            
            return redirect('lista_registros')
            
        except Exception as e:
            messages.error(request, f'Error al crear el registro: {str(e)}')
            registros = RegistroVisita.objects.all()
            return render(request, 'myapp/lista_registros.html', {
                'registros': registros
            })
    
    # 3. Manejar solicitudes GET (mostrar registros existentes)
    registros = RegistroVisita.objects.all().order_by('-fecha')
    return render(request, 'myapp/lista_registros.html', {
        'registros': registros
    })

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
        usuario = Usuario.objects.get(nombre_usuario=request.user.nombre_usuario)  
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
    - Incluye datos principales y la distribución por edades
    """
    registro = get_object_or_404(RegistroVisita, pk=id_registro)
    
    # Estructurar respuesta JSON con los nuevos campos
    data = {
        'id_registro': registro.id_registro,
        'fecha': registro.fecha.strftime('%Y-%m-%d %H:%M:%S') if registro.fecha else None,
        'estancia_dias': registro.estancia_dias,
        'visitas_previas': registro.visitas_previas,  # CAMPO AGREGADO
        'motivo_visita': registro.motivo_visita,
        'tipo_transporte': registro.tipo_transporte,
        'procedencia': registro.procedencia,
        'pais_origen': registro.pais_origen,
        'es_extranjero': registro.es_extranjero,
        'clave_encuestador': registro.clave_encuestador.clave_encuestador if registro.clave_encuestador else None,
        # Campos de distribución por edad y género
        'mujeres_0_15': registro.mujeres_0_15,
        'mujeres_16_30': registro.mujeres_16_30,
        'mujeres_31_45': registro.mujeres_31_45,
        'mujeres_46_60': registro.mujeres_46_60,
        'mujeres_61_75': registro.mujeres_61_75,
        'mujeres_76_mas': registro.mujeres_76_mas,
        'hombres_0_15': registro.hombres_0_15,
        'hombres_16_30': registro.hombres_16_30,
        'hombres_31_45': registro.hombres_31_45,
        'hombres_46_60': registro.hombres_46_60,
        'hombres_61_75': registro.hombres_61_75,
        'hombres_76_mas': registro.hombres_76_mas,
        # Totales calculados
        'total_mujeres': registro.total_mujeres,
        'total_hombres': registro.total_hombres,
        'total_personas': registro.total_personas,
    }
    return JsonResponse(data)

# Vista para editar un registro existente
@login_required
@transaction.atomic
def editar_registro(request, id_registro):
    """
    Vista para editar registros existentes:
    1. Verifica permisos del usuario
    2. Actualiza el registro principal con los nuevos campos
    """
    try:  
        usuario = Usuario.objects.get(nombre_usuario=request.user.nombre_usuario)  
        if usuario.tipo not in ['encuestador', 'admin']:  
            return HttpResponseForbidden("No tienes permiso para editar registros.")  
        
        if usuario.tipo == 'encuestador':  
            encuestador = Encuestador.objects.get(id_usuario=usuario)  
        else:  # admin  
            encuestador, created = Encuestador.objects.get_or_create(  
                id_usuario=usuario,
                defaults={
                    'clave_encuestador': usuario.id_usuario
                }  
            )  
    except Usuario.DoesNotExist:  
        return HttpResponse('Usuario no encontrado.', status=404)
    except Encuestador.DoesNotExist:  
        return HttpResponse('Encuestador no encontrado.', status=404)

    # Obtener registro a editar
    registro = get_object_or_404(RegistroVisita, pk=id_registro)

    if request.method == 'GET':
        return JsonResponse({
            "id_registro": registro.id_registro,
            "es_extranjero": registro.es_extranjero,
            "pais_origen": registro.pais_origen or "",
            "procedencia": registro.procedencia or "",
            "tipo_transporte": registro.tipo_transporte,
            "motivo_visita": registro.motivo_visita,
            "estancia_dias": registro.estancia_dias,
            "visitas_previas": registro.visitas_previas,

            # Mujeres
            "mujeres_0_15": registro.mujeres_0_15,
            "mujeres_16_30": registro.mujeres_16_30,
            "mujeres_31_45": registro.mujeres_31_45,
            "mujeres_46_60": registro.mujeres_46_60,
            "mujeres_61_75": registro.mujeres_61_75,
            "mujeres_76_mas": registro.mujeres_76_mas,

            # Hombres
            "hombres_0_15": registro.hombres_0_15,
            "hombres_16_30": registro.hombres_16_30,
            "hombres_31_45": registro.hombres_31_45,
            "hombres_46_60": registro.hombres_46_60,
            "hombres_61_75": registro.hombres_61_75,
            "hombres_76_mas": registro.hombres_76_mas,
        })
    if request.method == 'POST':
        # Función para conversión segura a enteros
        def to_int(value, default=None):
            try:
                return int(value)
            except (TypeError, ValueError):
                return default

        # Procesar datos del formulario
        es_extranjero = request.POST.get('es_extranjero') == '1'
        estancia_dias = to_int(request.POST.get('estancia_dias'), default=1)
        visitas_previas = to_int(request.POST.get('visitas_previas'), default=1)  # CAMPO AGREGADO
        motivo_visita = request.POST.get('motivo_visita', 'turismo')
        tipo_transporte = request.POST.get('tipo_transporte', 'automovil')
        procedencia = request.POST.get('procedencia', '')
        pais_origen = request.POST.get('pais_origen') if es_extranjero else None
        
        # Obtener valores de la tabla de edades y géneros
        mujeres_0_15 = to_int(request.POST.get('mujeres_0_15'), 0)
        mujeres_16_30 = to_int(request.POST.get('mujeres_16_30'), 0)
        mujeres_31_45 = to_int(request.POST.get('mujeres_31_45'), 0)
        mujeres_46_60 = to_int(request.POST.get('mujeres_46_60'), 0)
        mujeres_61_75 = to_int(request.POST.get('mujeres_61_75'), 0)
        mujeres_76_mas = to_int(request.POST.get('mujeres_76_mas'), 0)
        
        hombres_0_15 = to_int(request.POST.get('hombres_0_15'), 0)
        hombres_16_30 = to_int(request.POST.get('hombres_16_30'), 0)
        hombres_31_45 = to_int(request.POST.get('hombres_31_45'), 0)
        hombres_46_60 = to_int(request.POST.get('hombres_46_60'), 0)
        hombres_61_75 = to_int(request.POST.get('hombres_61_75'), 0)
        hombres_76_mas = to_int(request.POST.get('hombres_76_mas'), 0)
        
        # Calcular el total de personas
        total_mujeres = sum([
            mujeres_0_15, mujeres_16_30, mujeres_31_45, 
            mujeres_46_60, mujeres_61_75, mujeres_76_mas
        ])
        
        total_hombres = sum([
            hombres_0_15, hombres_16_30, hombres_31_45,
            hombres_46_60, hombres_61_75, hombres_76_mas
        ])
        
        total_personas = total_mujeres + total_hombres
        
        # Validar que haya al menos una persona
        if total_personas == 0:
            messages.error(request, 'Debe ingresar al menos una persona para actualizar.')
            return redirect('editar_registro', id_registro=id_registro)
        
        try:
            # Actualizar registro principal con los nuevos campos
            registro.es_extranjero = es_extranjero
            registro.pais_origen = pais_origen
            registro.procedencia = procedencia
            registro.tipo_transporte = tipo_transporte
            registro.motivo_visita = motivo_visita
            registro.estancia_dias = estancia_dias
            registro.visitas_previas = visitas_previas  # CAMPO AGREGADO
            registro.clave_encuestador = encuestador  # Mantener el encuestador original o actualizar si es admin
            
            # Actualizar campos de distribución por edad y género
            registro.mujeres_0_15 = mujeres_0_15
            registro.mujeres_16_30 = mujeres_16_30
            registro.mujeres_31_45 = mujeres_31_45
            registro.mujeres_46_60 = mujeres_46_60
            registro.mujeres_61_75 = mujeres_61_75
            registro.mujeres_76_mas = mujeres_76_mas
            
            registro.hombres_0_15 = hombres_0_15
            registro.hombres_16_30 = hombres_16_30
            registro.hombres_31_45 = hombres_31_45
            registro.hombres_46_60 = hombres_46_60
            registro.hombres_61_75 = hombres_61_75
            registro.hombres_76_mas = hombres_76_mas
            
            registro.save()
            return redirect('lista_registros')
            
        except Exception as e:
            messages.error(request, f'Error al actualizar el registro: {str(e)}')
            return redirect('editar_registro', id_registro=id_registro)
    
    

@transaction.atomic  
def formulario(request):  
    """  
    Vista específica para que encuestadores, administradores y usuarios independientes puedan crear registros  
    """
    encuestador = None
    if request.user.is_authenticated:
        try:  
            usuario = Usuario.objects.get(nombre_usuario=request.user.nombre_usuario)  
            if usuario.tipo not in ['encuestador', 'admin', 'propietario']:  
                return HttpResponseForbidden("No tienes permiso para acceder a esta página.")  
              
            if usuario.tipo == 'encuestador':  
                encuestador = Encuestador.objects.get(id_usuario=usuario)  
            else:  # admin o propietario  
                encuestador, _ = Encuestador.objects.get_or_create(id_usuario=usuario)  
        except (Usuario.DoesNotExist, Encuestador.DoesNotExist):  
            return HttpResponse('Usuario o encuestador no encontrado.', status=404)  
    else:
        # Usuario no autenticado (Independiente)
        try:
            usuario_indep, created = Usuario.objects.get_or_create(
                nombre_usuario='independiente',
                defaults={
                    'nombre': 'Independiente',
                    'ap': 'Visitante',
                    'email': 'independiente@observatorio.local',
                    'tipo': 'encuestador'
                }
            )
            if created:
                usuario_indep.set_password('observatorio_indep_123')
                usuario_indep.save()
            
            encuestador, _ = Encuestador.objects.get_or_create(id_usuario=usuario_indep)
        except Exception as e:
            return HttpResponse(f'Error al configurar acceso independiente: {e}', status=500)
  
    if request.method == 'POST':  
        # Función auxiliar para convertir valores a entero
        def to_int(value, default=None):  
            try:  
                return int(value)  
            except (TypeError, ValueError):  
                return default
  
        # Obtener valores del formulario
        es_extranjero = request.POST.get('es_extranjero') == '1'
        estancia_dias = to_int(request.POST.get('estancia_dias'), default=1)
        visitas_previas = to_int(request.POST.get('visitas_previas'), default=1)  # CAMPO AGREGADO
        motivo_visita = request.POST.get('motivo_visita') or 'turismo'
        tipo_transporte = request.POST.get('tipo_transporte') or 'automovil'
        procedencia = request.POST.get('procedencia')
        pais_origen = request.POST.get('pais_origen') if es_extranjero else None
        
        # Obtener valores de la tabla de edades y géneros
        mujeres_0_15 = to_int(request.POST.get('mujeres_0_15'), 0)
        mujeres_16_30 = to_int(request.POST.get('mujeres_16_30'), 0)
        mujeres_31_45 = to_int(request.POST.get('mujeres_31_45'), 0)
        mujeres_46_60 = to_int(request.POST.get('mujeres_46_60'), 0)
        mujeres_61_75 = to_int(request.POST.get('mujeres_61_75'), 0)
        mujeres_76_mas = to_int(request.POST.get('mujeres_76_mas'), 0)
        
        hombres_0_15 = to_int(request.POST.get('hombres_0_15'), 0)
        hombres_16_30 = to_int(request.POST.get('hombres_16_30'), 0)
        hombres_31_45 = to_int(request.POST.get('hombres_31_45'), 0)
        hombres_46_60 = to_int(request.POST.get('hombres_46_60'), 0)
        hombres_61_75 = to_int(request.POST.get('hombres_61_75'), 0)
        hombres_76_mas = to_int(request.POST.get('hombres_76_mas'), 0)
        
        # Calcular el total de personas
        total_mujeres = sum([
            mujeres_0_15, mujeres_16_30, mujeres_31_45, 
            mujeres_46_60, mujeres_61_75, mujeres_76_mas
        ])
        
        total_hombres = sum([
            hombres_0_15, hombres_16_30, hombres_31_45,
            hombres_46_60, hombres_61_75, hombres_76_mas
        ])
        
        total_personas = total_mujeres + total_hombres
        
        # Validar que haya al menos una persona
        if total_personas == 0:
            messages.error(request, 'Debe ingresar al menos una persona para registrar.')
            return render(request, 'myapp/formulario.html')
        
        # Validar campos numéricos
        if estancia_dias < 1 or estancia_dias > 255:
            messages.error(request, 'La estancia en días debe estar entre 1 y 255.')
            return render(request, 'myapp/formulario.html')
            
        if visitas_previas < 1 or visitas_previas > 255:
            messages.error(request, 'Las visitas previas deben estar entre 1 y 255.')
            return render(request, 'myapp/formulario.html')
        
        try:
            # Crear registro en la tabla Registro_visita
            registro = RegistroVisita.objects.create(
                estancia_dias=estancia_dias,
                visitas_previas=visitas_previas,  # CAMPO AGREGADO
                motivo_visita=motivo_visita,
                tipo_transporte=tipo_transporte,
                procedencia=procedencia,
                pais_origen=pais_origen,
                es_extranjero=es_extranjero,
                clave_encuestador=encuestador,
                # Campos de distribución por edad y género
                mujeres_0_15=mujeres_0_15,
                mujeres_16_30=mujeres_16_30,
                mujeres_31_45=mujeres_31_45,
                mujeres_46_60=mujeres_46_60,
                mujeres_61_75=mujeres_61_75,
                mujeres_76_mas=mujeres_76_mas,
                hombres_0_15=hombres_0_15,
                hombres_16_30=hombres_16_30,
                hombres_31_45=hombres_31_45,
                hombres_46_60=hombres_46_60,
                hombres_61_75=hombres_61_75,
                hombres_76_mas=hombres_76_mas
            )
            
            return redirect('formulario')
            
        except Exception as e:
            messages.error(request, f'Error al crear el registro: {str(e)}')
            return render(request, 'myapp/formulario.html')
    
    # Si es GET, mostrar el formulario vacío
    return render(request, 'myapp/formulario.html')

@login_required  
def eliminar_registro(request, id_registro):  
    """  
    Vista para eliminar un registro individual  
    """  
    # Verificar permisos  
    try:  
        usuario = Usuario.objects.get(nombre_usuario=request.user.nombre_usuario)  
        if usuario.tipo not in ['encuestador', 'admin']:  
            return HttpResponseForbidden("No tienes permiso para eliminar registros.")  
    except Usuario.DoesNotExist:  
        return HttpResponse('Usuario no encontrado.', status=404)  
      
    registro = get_object_or_404(RegistroVisita, pk=id_registro)  
      
    try:  
        registro.delete()  
    except Exception as e:  
        messages.error(request, f'Error al eliminar registro {id_registro}: {str(e)}')  
      
    return redirect('lista_registros')

# Vista para eliminación múltiple de registros
@login_required  
def eliminar_seleccionados(request):  
    """  
    Elimina múltiples registros seleccionados  
    """  
    ids_str = request.GET.get('ids', '')  
    if not ids_str:  
        messages.error(request, "No se seleccionaron registros para eliminar")
        return redirect('lista_registros')
      
    try:    
        usuario = Usuario.objects.get(nombre_usuario=request.user.nombre_usuario)    
        if usuario.tipo not in ['encuestador', 'admin']:    
            return HttpResponseForbidden("No tienes permiso para eliminar registros.")    
    except Usuario.DoesNotExist:    
        return HttpResponse('Usuario no encontrado.', status=404)  
      
    try:  
        # Convertir string de IDs a lista de enteros  
        ids = [int(id) for id in ids_str.split(',')]  
          
        # Eliminar registros  
        count, _ = RegistroVisita.objects.filter(id_registro__in=ids).delete()
        
        if count == 0:
            messages.warning(request, 'No se encontraron registros para eliminar')
            
    except Exception as e:  
        messages.error(request, f'Error al eliminar registros: {str(e)}')  
      
    return redirect('lista_registros')





#-------------Documentos - Repositorio----------------#


# ==============================================
# VISTAS PARA ADMINISTRADORES (Panel de control)
# ==============================================
@login_required
def panel_documentos(request):
    User = get_user_model()

    # Obtener parámetros de filtrado y ordenamiento
    categoria_id = request.GET.get('categoria', '')
    es_publico_filtro = request.GET.get('es_publico', '')
    sort_by = request.GET.get('sort', 'fecha_subida')
    order = request.GET.get('order', 'desc')
    search = request.GET.get('search', '')
    
    # Base queryset
    documentos = Documento.objects.all()
    
    # Aplicar filtro por categoría
    if categoria_id:
        documentos = documentos.filter(categoria_id=categoria_id)

    # Aplicar filtro por visibilidad
    if es_publico_filtro in ['True', 'False']:
        is_pub = True if es_publico_filtro == 'True' else False
        documentos = documentos.filter(es_publico=is_pub)
    
    # Aplicar búsqueda
    if search:
        documentos = documentos.filter(
            Q(titulo__icontains=search) |
            Q(descripcion__icontains=search)
        )
    
    # Aplicar ordenamiento
    valid_sorts = ['titulo', 'fecha_subida', 'tamaño', 'descargas']
    if sort_by in valid_sorts:
        if order == 'desc':
            sort_by = f'-{sort_by}'
        documentos = documentos.order_by(sort_by)
    
    # Paginación
    paginator = Paginator(documentos, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    admins = User.objects.filter(tipo='admin')
    categorias = Categoria.objects.all()
    tipos_choices = Documento._meta.get_field('tipo').choices
    
    context = {
        'documentos': page_obj,
        'administradores': admins,
        'categorias': categorias,
        'tipos_choices': tipos_choices,
        'sort_by': sort_by.replace('-', ''),
        'order': order,
        'categoria_filtro': categoria_id,
        'es_publico_filtro': es_publico_filtro,
        'search': search,
    }
    
    return render(request, 'myapp/lista_documentos.html', context)



@login_required
def subir_documento(request):
    if request.method == 'POST':
        try:
            titulo = request.POST.get('titulo', '').strip()
            descripcion = request.POST.get('descripcion', '').strip()
            clasificacion = request.POST.get('clasificacion')
            tipo = request.POST.get('tipo', 'reporte')
            
            # Categoria handling
            categoria_id = request.POST.get('categoria')
            categoria = None
            if categoria_id:
                try:
                    categoria = Categoria.objects.get(id=categoria_id)
                except Categoria.DoesNotExist:
                    pass
            
            archivo = request.FILES.get('archivo')
            url = request.POST.get('url', '').strip()
            
            if not titulo or not clasificacion:
                messages.error(request, 'Título y Clasificación son obligatorios')
                return redirect('panel_documentos')
            
            if not archivo and not url:
                messages.error(request, 'Debes subir un archivo físico o proporcionar una URL')
                return redirect('panel_documentos')
            
            # Crear instancia
            documento = Documento(
                titulo=titulo,
                descripcion=descripcion,
                clasificacion=clasificacion,
                tipo=tipo,
                categoria=categoria,
                es_publico=(clasificacion == 'publico'),
                clave_admin=request.user
            )
            
            if archivo:
                documento.archivo = archivo
                documento.save()  # Guarda y calcula tamaño y tipo
                documento.url = documento.archivo.url
            else:
                if not url.startswith(('http://', 'https://')):
                    messages.error(request, 'La URL debe comenzar con http:// o https://')
                    return redirect('panel_documentos')
                documento.url = url
            
            documento.save()
            messages.success(request, f'Documento "{titulo}" creado exitosamente')
            
        except Exception as e:
            print(f"Error detallado: {e}")
            messages.error(request, f'Error al crear documento: {str(e)}')
        
        return redirect('panel_documentos')
    
    return redirect('panel_documentos')

@login_required
def editar_documento(request, id):
    documento = get_object_or_404(Documento, id=id)

    if request.method == 'POST':
        try:
            documento.titulo = request.POST.get('titulo', '').strip()
            documento.descripcion = request.POST.get('descripcion', '').strip()
            documento.clasificacion = request.POST.get('clasificacion')
            documento.tipo = request.POST.get('tipo')
            documento.es_publico = (documento.clasificacion == 'publico')
            
            categoria_id = request.POST.get('categoria')
            if categoria_id:
                try:
                    documento.categoria = Categoria.objects.get(id=categoria_id)
                except Categoria.DoesNotExist:
                    documento.categoria = None
            else:
                documento.categoria = None

            archivo = request.FILES.get('archivo')
            url = request.POST.get('url', '').strip()
            
            if archivo:
                # Eliminar archivo físico anterior si existe
                if documento.archivo:
                    try:
                        if os.path.isfile(documento.archivo.path):
                            os.remove(documento.archivo.path)
                    except Exception as e:
                        print(f"Error al eliminar archivo anterior: {e}")
                documento.archivo = archivo
                documento.save()  # Triggers save() hook
                documento.url = documento.archivo.url
            elif url:
                if not url.startswith(('http://', 'https://')):
                    return JsonResponse({'success': False, 'error': 'La URL debe comenzar con http:// o https://'})
                documento.url = url
                # Si cambian a URL y tenían archivo físico, opcionalmente lo removemos
                if documento.archivo:
                    try:
                        if os.path.isfile(documento.archivo.path):
                            os.remove(documento.archivo.path)
                    except Exception as e:
                        print(f"Error al remover archivo: {e}")
                    documento.archivo = None
                    documento.tamaño = 0

            documento.clave_admin = request.user
            documento.save()
            
            return JsonResponse({'success': True, 'message': 'Actualizado correctamente'})

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    categorias = Categoria.objects.all()
    return render(request, 'myapp/editar_documento.html', {
        'documento': documento,
        'categorias': categorias,
        'tipos_choices': Documento._meta.get_field('tipo').choices,
        'clasificacion_choices': Documento._meta.get_field('clasificacion').choices
    })
    
@login_required
@require_http_methods(["POST"])
def eliminar_documento(request, id):
    """Vista para eliminar documento (AJAX)"""
    try:
        documento = get_object_or_404(Documento, id=id)
        titulo = documento.titulo
        
        # Eliminar archivo físico del disco si existe
        if documento.archivo:
            try:
                if os.path.isfile(documento.archivo.path):
                    os.remove(documento.archivo.path)
            except Exception as e:
                print(f"Error al eliminar archivo físico: {e}")
                
        documento.delete()
        
        return JsonResponse({
            'success': True,
            'mensaje': f'Documento "{titulo}" eliminado correctamente',
            'message': f'Documento "{titulo}" eliminado correctamente'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })

def descargar_documento(request, id):
    """Vista para descargar un documento (físico o URL externa)"""
    documento = get_object_or_404(Documento, id=id)
    
    # Verificar permisos
    if documento.clasificacion == 'publico':
        pass
    elif documento.clasificacion == 'privado' and not request.user.is_authenticated:
        messages.error(request, 'Debes iniciar sesión para descargar este documento')
        return redirect('login') + f'?next={request.path}'
    elif documento.clasificacion == 'confidencial' and not (request.user.is_authenticated and (request.user.is_superuser or (hasattr(request.user, 'tipo') and request.user.tipo == 'admin'))):
        messages.error(request, 'No tienes permiso para descargar este documento')
        return redirect('repositorio')
    
    # Incrementar descargas
    documento.descargas += 1
    documento.save(update_fields=['descargas'])
    
    # Servir archivo local si existe
    if documento.archivo:
        try:
            if os.path.exists(documento.archivo.path):
                response = FileResponse(
                    open(documento.archivo.path, 'rb'),
                    as_attachment=True,
                    filename=os.path.basename(documento.archivo.name)
                )
                return response
            else:
                messages.error(request, 'El archivo físico no se encuentra en el servidor')
                return redirect('repositorio')
        except Exception as e:
            messages.error(request, f'Error al descargar el archivo: {str(e)}')
            return redirect('repositorio')
            
    # Redirigir a URL externa si no hay archivo local
    if documento.url:
        return redirect(documento.url)
        
    messages.error(request, 'El documento no tiene un recurso asociado.')
    return redirect('repositorio')

# ==============================================
# VISTAS ADICIONALES SIMPLIFICADAS
# ==============================================

@login_required
def ver_documento_detalle(request, id):
    """Vista para ver detalles completos de un documento"""
    documento = get_object_or_404(Documento, id=id)
    
    # Verificar permisos de acceso
    if documento.clasificacion == 'privado' and not request.user.is_authenticated:
        messages.warning(request, 'Debes iniciar sesión para acceder a este documento')
        return redirect('login') + f'?next={request.path}'
    elif documento.clasificacion == 'confidencial' and not (request.user.is_superuser or (hasattr(request.user, 'tipo') and request.user.tipo == 'admin')):
        messages.error(request, 'No tienes permiso para acceder a este documento')
        return redirect('repositorio')
    
    context = {
        'documento': documento,
        'puede_editar': request.user.is_superuser or (hasattr(request.user, 'tipo') and request.user.tipo == 'admin'),
        'puede_eliminar': request.user.is_superuser or (hasattr(request.user, 'tipo') and request.user.tipo == 'admin'),
    }
    
    return render(request, 'myapp/detalle_documento.html', context)

# ==============================================
# VISTAS BASADAS EN CLASES SIMPLIFICADAS
# ==============================================

class DocumentoListView(LoginRequiredMixin, ListView):
    """Vista basada en clase para listar documentos (admin)"""
    model = Documento
    template_name = 'myapp/lista_documentos.html'
    context_object_name = 'documentos'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtros
        clasificacion = self.request.GET.get('clasificacion')
        if clasificacion and clasificacion in ['publico', 'privado', 'confidencial']:
            queryset = queryset.filter(clasificacion=clasificacion)
        
        # Búsqueda
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(titulo__icontains=search) |
                Q(descripcion__icontains=search)
            )
        
        # Ordenamiento
        sort_by = self.request.GET.get('sort', '-fecha_carga')
        if sort_by.lstrip('-') in ['titulo', 'fecha_carga', 'clasificacion']:
            queryset = queryset.order_by(sort_by)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['administradores'] = User.objects.filter(tipo='admin')
        context['sort_by'] = self.request.GET.get('sort', 'fecha_carga').lstrip('-')
        context['order'] = 'desc' if self.request.GET.get('sort', '').startswith('-') else 'asc'
        context['clasificacion_filtro'] = self.request.GET.get('clasificacion', '')
        context['search'] = self.request.GET.get('search', '')
        return context

def obtener_estadisticas(request):
    """Función para obtener estadísticas de documentos"""
    estadisticas = {
        'total': Documento.objects.count(),
        'publicos': Documento.objects.filter(clasificacion='publico').count(),
        'privados': Documento.objects.filter(clasificacion='privado').count(),
        'confidenciales': Documento.objects.filter(clasificacion='confidencial').count(),
    }
    
    # Si el usuario no es admin, ajustar estadísticas visibles
    if not request.user.is_admin and not request.user.is_superuser:
        if not request.user.is_authenticated:
            estadisticas['total'] = estadisticas['publicos']
            estadisticas['privados'] = 0
            estadisticas['confidenciales'] = 0
        else:
            estadisticas['total'] = estadisticas['publicos'] + estadisticas['privados']
            estadisticas['confidenciales'] = 0
    
    return estadisticas


@login_required
def exportar_documentos_csv(request):
    """Exportar lista de documentos a CSV (solo para usuarios autenticados)"""
    import csv
    from django.http import HttpResponse
    
    # Solo usuarios staff/admin pueden exportar todos los documentos
    is_admin = request.user.is_superuser or (hasattr(request.user, 'tipo') and request.user.tipo == 'admin')
    if is_admin:
        documentos = Documento.objects.all().order_by('id')
        filename = "todos_documentos.csv"
    else:
        # Usuarios normales solo exportan documentos accesibles
        documentos = Documento.objects.filter(
            Q(clasificacion='publico') | 
            Q(clasificacion='privado')
        ).order_by('id')
        filename = "mis_documentos.csv"
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    writer = csv.writer(response)
    writer.writerow(['ID', 'Título', 'Clasificación', 'URL', 'Fecha Carga', 'Administrador'])
    
    for doc in documentos:
        # Se obtiene el nombre del admin de forma segura
        admin_nombre = ""
        if doc.clave_admin:
            if hasattr(doc.clave_admin, 'get_full_name'):
                admin_nombre = doc.clave_admin.get_full_name()
            else:
                admin_nombre = getattr(doc.clave_admin, 'nombre', str(doc.clave_admin))
                
        writer.writerow([
            doc.id,
            doc.titulo,
            doc.get_clasificacion_display(),
            doc.url,
            doc.fecha_subida.strftime('%Y-%m-%d') if doc.fecha_subida else '',
            admin_nombre
        ])
    
    return response



def mapa(request):
    archivo_id = request.GET.get('archivo_id')
    
    # NUEVA LÓGICA DE FILTRADO CORREGIDA
    if archivo_id:
        # CORRECCIÓN: Usamos 'punto_interes' sin el '_set' dentro del Q()
        query = Q(id_archivo_id=archivo_id) | Q(punto_interes__isnull=False)
        geometrias = GeometriaEspacial.objects.filter(query).distinct()

    else:
        geometrias = GeometriaEspacial.objects.all()

    # Optimizamos consultas
    geometrias = geometrias.prefetch_related(
        'punto_interes_set',
        'punto_interes_set__sitio_turistico',
        'punto_interes_set__sitio_turistico__id_categoria',
        'punto_interes_set__servicio',
        'punto_interes_set__ofrenda',
        'punto_interes_set__galeria_multimedia_set'
    )
    
    lista_geometrias = list(geometrias)
    
    # =================================================================
    # PASO 1: HUELLAS DIGITALES (Evitar duplicados)
    # =================================================================
    coords_con_punto = set()
    for geo in lista_geometrias:
        # Normalizamos la lectura de coordenadas para el hash
        try:
            c_raw = geo.coordenadas if isinstance(geo.coordenadas, (dict, list)) else json.loads(geo.coordenadas)
            if not isinstance(c_raw, (dict, list)): continue
            
            c_obj = None
            if geo.tipo == 'punto':
                if isinstance(c_raw, list): c_obj = c_raw
                elif isinstance(c_raw, dict) and 'coordinates' in c_raw: c_obj = c_raw['coordinates']
            elif geo.tipo == 'linea' and isinstance(c_raw, list): c_obj = c_raw
            elif (geo.tipo == 'poligono' or geo.tipo == 'multipoligono') and isinstance(c_raw, list): c_obj = c_raw
            
            if c_obj:
                # Si esta geometría tiene un Punto de Interés asociado en BD, guardamos su hash
                # (geo.punto_interes_set.exists() es la forma correcta de verificarlo)
                if geo.punto_interes_set.exists():
                    c_str = json.dumps(c_obj, sort_keys=True)
                    key = hashlib.md5(c_str.encode('utf-8')).hexdigest()
                    coords_con_punto.add(key)
        except Exception: pass

    # =================================================================
    # PASO 2: CONSTRUIR EL GEOJSON
    # =================================================================
    features = []

    for geo in lista_geometrias:
        if not geo.coordenadas:
            continue

        try:
            coords_raw = geo.coordenadas if isinstance(geo.coordenadas, (dict, list)) else json.loads(geo.coordenadas)
            
            # Determinar tipo de geometría GeoJSON y coord_key para el hash
            geometry_obj = None
            coord_key = None
            
            if geo.tipo == 'linea' and isinstance(coords_raw, list):
                geometry_obj = { "type": "LineString", "coordinates": coords_raw }
            elif geo.tipo == 'punto':
                if isinstance(coords_raw, list): geometry_obj = { "type": "Point", "coordinates": coords_raw }
                elif isinstance(coords_raw, dict) and 'coordinates' in coords_raw: geometry_obj = coords_raw
            elif geo.tipo == 'poligono' and isinstance(coords_raw, list):
                geometry_obj = { "type": "Polygon", "coordinates": coords_raw }
            elif geo.tipo == 'multipoligono' and isinstance(coords_raw, list):
                geometry_obj = { "type": "MultiPolygon", "coordinates": coords_raw }
            
            if not geometry_obj: continue

            # Generamos la huella digital para el elemento actual
            c_str = json.dumps(geometry_obj['coordinates'], sort_keys=True)
            coord_key = hashlib.md5(c_str.encode('utf-8')).hexdigest()

            punto = geo.punto_interes_set.first()
            
            
            if punto and punto.estado == 'inactivo':
                continue
            # LA MAGIA ESTÁ AQUÍ:
            # Si este elemento NO tiene un Punto de Interés, pero su huella digital coincide 
            # con una geometría que SÍ lo tiene (ej. el polígono del Zócalo administrado), lo descartamos.
            # Esto evita que el Zócalo crudo (general_kml) se muestre bajo el Zócalo administrado (sitio_turistico).
            if not punto and coord_key in coords_con_punto:
                continue

            # -- Resto de tu lógica para construir las propiedades (sin cambios) --
            extra_props = {}
            if geo.propiedades:
                try: extra_props = geo.propiedades if isinstance(geo.propiedades, dict) else json.loads(geo.propiedades)
                except json.JSONDecodeError: pass
            
            nombre_rescatado = extra_props.get('Nombre') or extra_props.get('nombre') or geo.nombre or "Sin nombre"
            cat_filtro_rescatada = "Corredores" if geo.tipo == 'linea' else "Otros"

            desc_rescatada = extra_props.get('descripcion') or extra_props.get('description') or ""
            if not desc_rescatada and extra_props:
                desc_rescatada = f"Datos extra: {json.dumps(extra_props)}"

            propiedades = {
                "id_geometria": geo.id_geometria,
                "nombre": nombre_rescatado,
                "categoria_filtro": cat_filtro_rescatada,
                "categoria_sistema": "general_kml", 
                "descripcion": desc_rescatada,
                "imagen": "",
                "horario": "Siempre abierto",
                "id_categoria_bd": None
            }

            if punto:
                nombre_filtro = "Otros"
                id_cat_bd = None
                
                if punto.categoria == 'sitio_turistico':
                    sitio = getattr(punto, 'sitio_turistico', None)
                    if sitio and sitio.id_categoria:
                        nombre_filtro = sitio.id_categoria.nombre
                        id_cat_bd = sitio.id_categoria.id_categoria
                    else: nombre_filtro = "Sitio Turístico"
                elif punto.categoria == 'ofrenda': nombre_filtro = "Ofrendas"
                elif punto.categoria == 'servicio': nombre_filtro = "Servicios"

                # Galería multimedia del punto
                galeria_items = [
                    {"url": g.url_archivo, "tipo": g.tipo_archivo}
                    for g in punto.galeria_multimedia_set.all()
                ]

                propiedades.update({
                    "id_punto": punto.id_punto,
                    "nombre": punto.nombre,
                    "categoria_filtro": nombre_filtro,
                    "categoria_sistema": punto.categoria,
                    "id_categoria_bd": id_cat_bd,
                    "descripcion": punto.descripcion or "",
                    "imagen": getattr(punto.imagen_portada, 'url', str(punto.imagen_portada)) if punto.imagen_portada else "",
                    "horario": f"{punto.hora_apertura} - {punto.hora_cierre}" if punto.hora_apertura and punto.hora_cierre else "Siempre abierto",
                    "galeria": galeria_items,
                    "ofrenda_anfitrion": "",
                })

                # Datos específicos por categoría
                if punto.categoria == 'ofrenda' and hasattr(punto, 'ofrenda'):
                    propiedades['ofrenda_anfitrion'] = punto.ofrenda.anfitrion or ""

                if punto.categoria == 'servicio' and hasattr(punto, 'servicio') and punto.servicio:
                    propiedades['contacto'] = punto.servicio.contacto or ""

            features.append({
                "type": "Feature",
                "geometry": geometry_obj,
                "properties": propiedades
            })

        except Exception as e:
            print(f"Error procesando geo {geo.id_geometria}: {e}")

    geojson_data = { "type": "FeatureCollection", "features": features }

    sitios_data = list(Sitio_turistico.objects.select_related('id_punto', 'id_categoria').values('id_sitio', 'id_punto__nombre', 'id_categoria__nombre'))
    ofrendas_data = list(Ofrenda.objects.select_related('id_punto').values('id_ofrenda', 'id_punto__nombre', 'anfitrion'))
    servicios_data = list(Servicio.objects.select_related('id_punto').values('id_servicio', 'id_punto__nombre', 'tipo_servicio', 'contacto'))

    context = {
        'geojson_data': json.dumps(geojson_data, default=str),
        'categorias_sitio': json.dumps(list(Categoria_Sitio.objects.values('id_categoria', 'nombre')), default=str),
        'sitios_turisticos': json.dumps(sitios_data, default=str),
        'ofrendas': json.dumps(ofrendas_data, default=str),
        'servicios': json.dumps(servicios_data, default=str),
        'recaptcha_site_key': settings.RECAPTCHA_SITE_KEY,
    }

    return render(request, 'mapa.html', context)



@login_required
def subir_desde_url(request):
    
    mis_categorias = Categoria_Sitio.objects.all().order_by('nombre')
    
    # Obtenemos la clase de tu usuario personalizado
    UsuarioCustom = get_user_model()
    
    context = {
        'categorias': mis_categorias, 
        'modo_edicion': False,
    }
    
    # --- 1. PREPARACIÓN DEL OBJETO ---
    archivo = None
    if request.method == 'POST':
        modo_ed = request.POST.get('modo_edicion') == 'true'
        archivo_id_post = request.POST.get('archivo_id_editar') or ''
        
        if modo_ed and archivo_id_post.strip().isdigit():
            try:
                archivo = ArchivoKMZ.objects.get(id_archivo=int(archivo_id_post), usuario=request.user)
            except ArchivoKMZ.DoesNotExist:
                archivo = None

    if archivo is None:
        archivo = ArchivoKMZ(usuario=request.user)

    # --- 2. PROCESAMIENTO ---
    if request.method == 'POST':
        try:
            # Datos del form
            archivo_url = request.POST.get('archivo_url')
            nombre_archivo = request.POST.get('nombre_archivo')
            
            if not archivo_url or not nombre_archivo:
                messages.error(request, 'URL y Nombre del archivo son obligatorios')
                return render(request, 'myapp/mod_db/upload_kml.html', context)

            with transaction.atomic():
                
                # A) ArchivoKMZ
                archivo.nombre_archivo = nombre_archivo
                archivo.archivo_path = archivo_url
                archivo.descripcion = request.POST.get('descripcion', '')
                extension = archivo_url.lower().strip()
                if extension.endswith('.kml'):
                    archivo.tipo_archivo = 'kml'
                elif extension.endswith('.kmz'):
                    archivo.tipo_archivo = 'kmz'
                else:
                    archivo.tipo_archivo = request.POST.get('tipo_archivo', 'kmz')
                archivo.visible = request.POST.get('visible') == 'on'
                archivo.procesado = False
                archivo.save()

                # B) Geometría
                geometria = GeometriaEspacial.objects.filter(id_archivo=archivo).first()
                if not geometria:
                    geometria = GeometriaEspacial.objects.create(
                        id_archivo=archivo,
                        nombre=nombre_archivo,
                        tipo='punto',
                        coordenadas={}
                    )
                else:
                    geometria.nombre = nombre_archivo
                    geometria.save()

                # C) Punto de Interés
                tipo_seleccionado = request.POST.get('tipo_punto', '') 

                if tipo_seleccionado:
                    punto = Punto_Interes.objects.filter(id_geometria=geometria).first()
                    
                    # Campos comunes
                    nombre_pto = request.POST.get('nombre_punto') or nombre_archivo
                    estado_pto = request.POST.get('estado_punto', 'activo')
                    f_ini = request.POST.get('fecha_inicio') or None
                    f_fin = request.POST.get('fecha_fin') or None
                    h_ape = request.POST.get('hora_apertura') or None
                    h_cie = request.POST.get('hora_cierre') or None
                    
                    # --- [CORRECCIÓN 1: IMAGEN PORTADA] ---
                    img_portada = ''
                    if 'imagen_portada' in request.FILES and request.FILES['imagen_portada']:
                        from django.core.files.storage import FileSystemStorage
                        fs = FileSystemStorage()
                        f_port = request.FILES['imagen_portada']
                        filename_port = fs.save(f"portadas/{f_port.name}", f_port)
                        img_portada = fs.url(filename_port)

                    # --- [CORRECCIÓN 2: DÍAS DE OPERACIÓN] ---
                    dias_lista = request.POST.getlist('dias_semana') # <-- Usar getlist
                    dias_str = ",".join(dias_lista) if dias_lista else ''

                    if not punto:
                        # CREAR
                        punto = Punto_Interes.objects.create(
                            id_geometria=geometria,
                            nombre=nombre_pto,
                            descripcion=archivo.descripcion,
                            estado=estado_pto,
                            fecha_inicio=f_ini,
                            fecha_fin=f_fin,
                            hora_apertura=h_ape,
                            hora_cierre=h_cie,
                            categoria=tipo_seleccionado,
                            usuario_creacion=request.user,
                            # Nuevos campos
                            imagen_portada=img_portada,
                            dias_semana=dias_str
                        )
                    else:
                        # ACTUALIZAR
                        punto.nombre = nombre_pto
                        punto.descripcion = archivo.descripcion
                        punto.estado = estado_pto
                        punto.fecha_inicio = f_ini
                        punto.fecha_fin = f_fin
                        punto.hora_apertura = h_ape
                        punto.hora_cierre = h_cie
                        punto.categoria = tipo_seleccionado
                        # Nuevos campos
                        punto.imagen_portada = img_portada
                        punto.dias_semana = dias_str
                        
                        # Integridad de usuario
                        if punto.usuario_creacion_id:
                            if not UsuarioCustom.objects.filter(pk=punto.usuario_creacion_id).exists():
                                punto.usuario_creacion = request.user
                        else:
                            punto.usuario_creacion = request.user
                            
                        punto.save()

                    # D) Subtipos (Sitio, Ofrenda, Servicio)
                    if tipo_seleccionado == 'sitio_turistico':
                        id_cat = request.POST.get('id_categoria_bd')
                        reglas = request.POST.get('reglas_acceso', '')
                        
                        if not id_cat:
                             raise Exception("Categoría obligatoria para sitios turísticos")
                        
                        cat_obj = Categoria_Sitio.objects.get(id_categoria=id_cat)
                        
                        if hasattr(punto, 'sitio_turistico'):
                            punto.sitio_turistico.id_categoria = cat_obj
                            punto.sitio_turistico.reglas_acceso = reglas
                            punto.sitio_turistico.save()
                        else:
                            Sitio_turistico.objects.create(id_punto=punto, id_categoria=cat_obj, reglas_acceso=reglas)
                        messages.success(request, f'Sitio Turístico ({cat_obj.nombre}) guardado.')

                    elif tipo_seleccionado == 'ofrenda':
                        anfitrion = request.POST.get('anfitrion', 'Sin anfitrión')
                        if hasattr(punto, 'ofrenda'):
                            punto.ofrenda.anfitrion = anfitrion
                            punto.ofrenda.save()
                        else:
                            Ofrenda.objects.create(id_punto=punto, anfitrion=anfitrion)
                        messages.success(request, 'Ofrenda guardada.')

                    elif tipo_seleccionado == 'servicio':
                        tipo_serv = request.POST.get('tipo_servicio', 'hospedaje')
                        contacto = request.POST.get('contacto_servicio', '')
                        
                        pagos_lista = request.POST.getlist('tipo_pago')
                        pagos = ",".join(pagos_lista) if pagos_lista else 'efectivo'
                        
                        if hasattr(punto, 'servicio'):
                            punto.servicio.tipo_servicio = tipo_serv
                            punto.servicio.contacto = contacto
                            punto.servicio.tipo_pago = pagos
                            punto.servicio.save()
                        else:
                            Servicio.objects.create(id_punto=punto, tipo_servicio=tipo_serv, contacto=contacto, tipo_pago=pagos)
                        messages.success(request, 'Servicio guardado.')
                    
                    # --- E) PROCESAR GALERÍA MULTIMEDIA ---
                    archivos_galeria = request.FILES.getlist('galeria_multimedia')
                    if archivos_galeria and punto:
                        from django.core.files.storage import FileSystemStorage # Importar aquí si no es global
                        fs = FileSystemStorage()
                        
                        for f in archivos_galeria:
                            ext = f.name.split('.')[-1].lower()
                            tipo = 'imagen'
                            if ext in ['mp4', 'avi', 'mov', 'webm']:
                                tipo = 'video'
                            elif ext in ['mp3', 'wav']:
                                tipo = 'audio'
                    
                            # Guardar archivo físico y obtener URL
                            filename = fs.save(f"galeria/{f.name}", f)
                            url_publica = fs.url(filename) 

                            Galeria_Multimedia.objects.create(
                                id_punto=punto,
                                url_archivo=url_publica, 
                                tipo_archivo=tipo,
                                descripcion=f"Subido el {timezone.now().date()}"
                            )
                else:
                    messages.success(request, 'Archivo guardado correctamente (sin detalles de punto).')
            
            return redirect('lista_archivos')

        except Exception as e:
            messages.error(request, f'Error al guardar: {str(e)}')
            return render(request, 'myapp/mod_db/crud_kml.html', context)

    return render(request, 'myapp/mod_db/crud_kml.html', context)

@login_required
def lista_archivos(request):
    categorias = Categoria_Sitio.objects.all()
    """Vista para listar archivos por URL"""
    # Obtener archivos del usuario (o todos si es superusuario)
    if request.user.is_superuser:
        archivos = ArchivoKMZ.objects.all()
    else:
        archivos = ArchivoKMZ.objects.filter(usuario=request.user)
    
    # Anotar con número de geometrías
    archivos = archivos.annotate(
        num_geometrias=Count('geometriaespacial')
    ).select_related('usuario')
    
    # Calcular estadísticas
    ahora = timezone.now()
    
    # Archivos visibles ahora (simplificado sin fechas)
    archivos_visibles = archivos.filter(visible=True).count()
    
    # Archivos por tipo
    archivos_kml_kmz = archivos.filter(tipo_archivo__in=['kml', 'kmz']).count()
    archivos_multimedia = archivos.filter(tipo_archivo__in=['imagen', 'video', 'audio']).count()
    archivos_otros = archivos.exclude(tipo_archivo__in=['kml', 'kmz', 'imagen', 'video', 'audio']).count()
    
    # Total de geometrías
    total_geometrias = GeometriaEspacial.objects.filter(
        id_archivo__in=archivos
    ).count()
    
    # Archivos procesados (solo aplica a KML/KMZ)
    archivos_procesados = archivos.filter(procesado=True).count()
    
    context = {
        'archivos': archivos,
        'archivos_visibles': archivos_visibles,
        'archivos_kml_kmz': archivos_kml_kmz,
        'archivos_multimedia': archivos_multimedia,
        'archivos_otros': archivos_otros,
        'total_geometrias': total_geometrias,
        'archivos_procesados': archivos_procesados,
        'ahora': ahora,
    }
    context['categorias'] = categorias

    # 2. Pasamos la variable 'context' COMPLETA al render
    return render(request, 'myapp/mod_db/crud_kml.html', context)


@login_required
def detalle_archivo(request, archivo_id):
    try:
        archivo = get_object_or_404(ArchivoKMZ, id_archivo=archivo_id, usuario=request.user)
        # VOLVEMOS AL .first() ORIGINAL
        punto = Punto_Interes.objects.filter(id_geometria__id_archivo=archivo).first()

        def format_date(dt):
            return dt.strftime('%Y-%m-%d') if dt else ''
        
        def format_time(t):
            return t.strftime('%H:%M') if t else ''

        # --- DATOS DEL ARCHIVO ---
        data = {
            'success': True,
            'id_archivo': archivo.id_archivo,
            'nombre_archivo': archivo.nombre_archivo,
            'descripcion': archivo.descripcion or '', 
            'visible': archivo.visible,
            'tipo_archivo': archivo.tipo_archivo,
            'archivo_path': archivo.archivo_path, 
            'tiene_punto': False,
            'galeria': [] 
        }

        # --- DATOS DEL PUNTO (Si existe) ---
        if punto:
            data.update({
                'tiene_punto': True,
                'id_punto': punto.id_punto,
                'nombre_punto': punto.nombre,
                'descripcion_punto': punto.descripcion or '',
                'estado_punto': punto.estado,
                'fecha_inicio': format_date(punto.fecha_inicio),
                'fecha_fin': format_date(punto.fecha_fin),
                'hora_apertura': format_time(punto.hora_apertura),
                'hora_cierre': format_time(punto.hora_cierre),
                'imagen_portada': punto.imagen_portada or '',
                'dias_semana': punto.dias_semana.split(',') if punto.dias_semana else [],
            })

            try:
                items_galeria = punto.galeria_multimedia_set.all() 
                galeria_data = []
                for item in items_galeria:
                    galeria_data.append({'id': item.id_foto, 'url': item.url_archivo, 'tipo': item.tipo_archivo})
                data['galeria'] = galeria_data
            except Exception:
                data['galeria'] = []

            # --- SUBTIPOS ---
            if hasattr(punto, 'sitio_turistico'):
                sitio = punto.sitio_turistico
                data.update({
                    'tipo_punto': 'sitio_turistico',
                    'id_categoria_bd': sitio.id_categoria.id_categoria if sitio.id_categoria else '',
                    'reglas_acceso': sitio.reglas_acceso or ''
                })
            elif hasattr(punto, 'ofrenda'):
                data.update({'tipo_punto': 'ofrenda', 'anfitrion': punto.ofrenda.anfitrion or ''})
            elif hasattr(punto, 'servicio'):
                servicio = punto.servicio
                data.update({
                    'tipo_punto': 'servicio',
                    'tipo_servicio': servicio.tipo_servicio,
                    'contacto_servicio': servicio.contacto or '',
                    'tipo_pago': servicio.tipo_pago.split(',') if servicio.tipo_pago else []
                })

        return JsonResponse(data)

    except Exception as e:
        return JsonResponse({'success': False, 'error': f"Error: {str(e)}"}, status=500)
    
@login_required
def editar_archivo(request, archivo_id):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Método no permitido'}, status=405)

    try:
        with transaction.atomic():
            # 1. Obtener y Actualizar el ArchivoKMZ base
            archivo = get_object_or_404(ArchivoKMZ, id_archivo=archivo_id, usuario=request.user)
            
            archivo.nombre_archivo = request.POST.get('nombre_archivo', archivo.nombre_archivo)
            archivo.descripcion = request.POST.get('descripcion', archivo.descripcion)
            archivo.tipo_archivo = request.POST.get('tipo_archivo', archivo.tipo_archivo)
            archivo.visible = request.POST.get('visible') == 'on'
            archivo.save()

            # 2. Actualizar Geometría
            geometria = GeometriaEspacial.objects.filter(id_archivo=archivo).first()
            if geometria:
                geometria.nombre = archivo.nombre_archivo
                geometria.save()

                # 3. Actualizar o Crear Punto de Interés
                punto = Punto_Interes.objects.filter(id_geometria=geometria).first()
                tipo_seleccionado = request.POST.get('tipo_punto', '')

                # Si el usuario seleccionó que ESTE archivo es un ofrenda, servicio o sitio:
                if tipo_seleccionado:
                    if not punto:
                        # Si no existía punto para este archivo, lo creamos
                        punto = Punto_Interes(id_geometria=geometria, usuario_creacion=request.user)

                    punto.nombre = request.POST.get('nombre_punto') or archivo.nombre_archivo
                    punto.descripcion = archivo.descripcion 
                    punto.estado = request.POST.get('estado_punto', 'activo')
                    
                    # Manejo seguro de fechas vacías
                    punto.fecha_inicio = request.POST.get('fecha_inicio') or None
                    punto.fecha_fin = request.POST.get('fecha_fin') or None
                    punto.hora_apertura = request.POST.get('hora_apertura') or None
                    punto.hora_cierre = request.POST.get('hora_cierre') or None

                    # --- IMAGEN DE PORTADA LOCAL ---
                    if 'imagen_portada' in request.FILES and request.FILES['imagen_portada']:
                        fs = FileSystemStorage()
                        f_port = request.FILES['imagen_portada']
                        filename_port = fs.save(f"portadas/{f_port.name}", f_port)
                        punto.imagen_portada = fs.url(filename_port)

                    # --- DIAS DE LA SEMANA ---
                    dias_lista = request.POST.getlist('dias_semana')
                    if dias_lista:
                        punto.dias_semana = ",".join(dias_lista)
                    elif 'dias_semana' in request.POST:
                        punto.dias_semana = ''

                    punto.categoria = tipo_seleccionado
                    punto.save()

                    # 4. Actualizar Subtipos (get_or_create evita errores si antes no existían)
                    if tipo_seleccionado == 'sitio_turistico':
                        id_cat = request.POST.get('id_categoria_bd')
                        reglas = request.POST.get('reglas_acceso', '')
                        if id_cat:
                            cat_obj = Categoria_Sitio.objects.get(id_categoria=id_cat)
                            sitio_obj, created = Sitio_turistico.objects.get_or_create(id_punto=punto, defaults={'id_categoria': cat_obj, 'reglas_acceso': reglas})
                            if not created:
                                sitio_obj.id_categoria = cat_obj
                                sitio_obj.reglas_acceso = reglas
                                sitio_obj.save()

                    elif tipo_seleccionado == 'ofrenda':
                        anfitrion = request.POST.get('anfitrion', 'Sin anfitrión')
                        ofr_obj, created = Ofrenda.objects.get_or_create(id_punto=punto, defaults={'anfitrion': anfitrion})
                        if not created:
                            ofr_obj.anfitrion = anfitrion
                            ofr_obj.save()

                    elif tipo_seleccionado == 'servicio':
                        tipo_serv = request.POST.get('tipo_servicio', 'hospedaje')
                        contacto = request.POST.get('contacto_servicio', '')
                        pagos_lista = request.POST.getlist('tipo_pago')
                        pagos_str = ",".join(pagos_lista) if pagos_lista else 'efectivo'
                        
                        serv_obj, created = Servicio.objects.get_or_create(id_punto=punto, defaults={'tipo_servicio': tipo_serv, 'contacto': contacto, 'tipo_pago': pagos_str})
                        if not created:
                            serv_obj.tipo_servicio = tipo_serv
                            serv_obj.contacto = contacto
                            serv_obj.tipo_pago = pagos_str
                            serv_obj.save()

                    # --- 5. GALERIA MULTIMEDIA ---
                    archivos_galeria = request.FILES.getlist('galeria_multimedia')
                    if archivos_galeria:
                        fs = FileSystemStorage()
                        for f in archivos_galeria:
                            ext = f.name.split('.')[-1].lower()
                            tipo = 'video' if ext in ['mp4', 'avi', 'mov', 'webm'] else 'audio' if ext in ['mp3', 'wav'] else 'imagen'
                            
                            filename = fs.save(f"galeria/{f.name}", f)
                            Galeria_Multimedia.objects.create(
                                id_punto=punto,
                                url_archivo=fs.url(filename),
                                tipo_archivo=tipo,
                                descripcion=f"Subido el {timezone.now().date()}"
                            )

                    # Eliminar fotos de galería marcadas con la "X"
                    ids_eliminar = request.POST.getlist('galeria_eliminar')
                    if ids_eliminar:
                        Galeria_Multimedia.objects.filter(id_foto__in=ids_eliminar, id_punto=punto).delete()

        return JsonResponse({'success': True, 'message': 'Archivo actualizado correctamente.'})

    except ArchivoKMZ.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'El archivo no existe o no tienes permiso.'}, status=404)
    except Exception as e:
        import traceback
        traceback.print_exc() # Esto imprimirá el error real en la terminal de Docker
        return JsonResponse({'success': False, 'error': f'Error interno: {str(e)}'}, status=400)





################  Punto de Interés  ################
# ==========================================================
# 1. VISTA DE LISTA PRINCIPAL
# ==========================================================

@login_required
def lista_puntos(request):
    puntos = Punto_Interes.objects.select_related('id_geometria', 'usuario_creacion').all()
    categorias = Categoria_Sitio.objects.all()
    
    context = {
        'puntos': puntos,
        'categorias': categorias, # <- Lo enviamos al template
        'total_activos': puntos.filter(estado='activo').count(),
        'total_inactivos': puntos.filter(estado='inactivo').count(),
        'total_ofrendas': puntos.filter(categoria='ofrenda').count(),
        'total_sitios': puntos.filter(categoria='sitio_turistico').count(),
    }
    return render(request, 'myapp/mod_db/crud_punto_interes.html', context)

# ==========================================================
# 2. VISTA PARA EL TOGGLE DE VISIBILIDAD (Activo/Inactivo)
# ==========================================================
@login_required
@require_POST
def toggle_visibilidad(request, punto_id):
    """Cambia el estado de un punto entre 'activo' e 'inactivo' mediante AJAX"""
    try:
        punto = get_object_or_404(Punto_Interes, id_punto=punto_id)
        
        # Leemos el JSON que envía el frontend (el switch)
        data = json.loads(request.body)
        es_activo = data.get('activo', False)
        
        # Asignamos el estado usando tu ESTADO_CHOICES
        punto.estado = 'activo' if es_activo else 'inactivo'
        punto.save()
        
        return JsonResponse({
            'success': True, 
            'nuevo_estado': punto.estado,
            'message': f'Estado actualizado a {punto.get_estado_display()}'
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


# ==========================================================
# 3. VISTA PARA OBTENER DATOS DEL PUNTO (Para rellenar el Modal)
# ==========================================================
# ==========================================================
# 3. VISTA PARA OBTENER DATOS DEL PUNTO (Para rellenar el Modal)
# ==========================================================
@login_required
def detalle_punto(request, punto_id):
    """Devuelve un JSON con los datos del punto para llenar el formulario de edición"""
    try:
        punto = get_object_or_404(Punto_Interes, id_punto=punto_id)

        fmt_date = lambda d: d.strftime('%Y-%m-%d') if d else ''
        fmt_time = lambda t: t.strftime('%H:%M') if t else ''

        # Galería multimedia existente
        galeria = [
            {'id': g.id_foto, 'url': g.url_archivo, 'tipo': g.tipo_archivo}
            for g in punto.galeria_multimedia_set.all()
        ]

        data = {
            'success': True,
            'id_punto': punto.id_punto,
            'categoria': punto.categoria,
            'nombre': punto.nombre,
            'descripcion': punto.descripcion or '',
            # Modificación segura para proteger la serialización JSON
            'imagen_portada': getattr(punto.imagen_portada, 'url', str(punto.imagen_portada)) if punto.imagen_portada else '',
            'estado': punto.estado,
            'fecha_inicio': fmt_date(punto.fecha_inicio),
            'fecha_fin': fmt_date(punto.fecha_fin),
            'hora_apertura': fmt_time(punto.hora_apertura),
            'hora_cierre': fmt_time(punto.hora_cierre),
            'dias_semana': punto.dias_semana_list,
            'galeria': galeria,
        }

        if hasattr(punto, 'ofrenda'):
            data['anfitrion'] = punto.ofrenda.anfitrion or ''
        elif hasattr(punto, 'sitio_turistico'):
            sitio = punto.sitio_turistico
            data['id_categoria_bd'] = sitio.id_categoria.id_categoria if sitio.id_categoria else ''
            data['reglas_acceso'] = sitio.reglas_acceso or ''
        elif hasattr(punto, 'servicio'):
            servicio = punto.servicio
            data['tipo_servicio'] = servicio.tipo_servicio or ''
            data['contacto_servicio'] = servicio.contacto or ''
            data['tipo_pago'] = servicio.tipo_pago.split(',') if servicio.tipo_pago else []

        return JsonResponse(data)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


# ==========================================================
# 4. VISTA PARA GUARDAR LA EDICIÓN
# ==========================================================
@login_required
@require_POST
def editar_punto(request, punto_id):
    """Recibe los datos del Modal vía POST y actualiza el registro"""
    try:
        punto = get_object_or_404(Punto_Interes, id_punto=punto_id)

        # 1. Campos básicos del Punto_Interes
        punto.nombre = request.POST.get('nombre_punto', punto.nombre)
        punto.categoria = request.POST.get('categoria', punto.categoria)
        punto.descripcion = request.POST.get('descripcion', '')
        if 'imagen_portada' in request.FILES and request.FILES['imagen_portada']:
            from django.core.files.storage import FileSystemStorage
            fs = FileSystemStorage()
            f_port = request.FILES['imagen_portada']
            filename_port = fs.save(f"portadas/{f_port.name}", f_port)
            punto.imagen_portada = fs.url(filename_port)

        fecha_inicio = request.POST.get('fecha_inicio')
        punto.fecha_inicio = fecha_inicio if fecha_inicio else None

        fecha_fin = request.POST.get('fecha_fin')
        punto.fecha_fin = fecha_fin if fecha_fin else None

        hora_apertura = request.POST.get('hora_apertura')
        punto.hora_apertura = hora_apertura if hora_apertura else None

        hora_cierre = request.POST.get('hora_cierre')
        punto.hora_cierre = hora_cierre if hora_cierre else None

        dias_seleccionados = request.POST.getlist('dias_semana')
        punto.dias_semana_list = dias_seleccionados
        punto.save()

        # 2. Submodelos según categoría
        categoria = punto.categoria

        if categoria == 'ofrenda':
            anfitrion = request.POST.get('anfitrion', '').strip()
            if hasattr(punto, 'ofrenda'):
                punto.ofrenda.anfitrion = anfitrion
                punto.ofrenda.save()
            else:
                Ofrenda.objects.create(id_punto=punto, anfitrion=anfitrion)

        elif categoria == 'sitio_turistico':
            id_cat = request.POST.get('id_categoria_bd')
            reglas = request.POST.get('reglas_acceso', '')
            if id_cat:
                cat_obj = Categoria_Sitio.objects.get(id_categoria=id_cat)
                if hasattr(punto, 'sitio_turistico'):
                    punto.sitio_turistico.id_categoria = cat_obj
                    punto.sitio_turistico.reglas_acceso = reglas
                    punto.sitio_turistico.save()
                else:
                    Sitio_turistico.objects.create(id_punto=punto, id_categoria=cat_obj, reglas_acceso=reglas)

        elif categoria == 'servicio':
            tipo_servicio_val = request.POST.get('tipo_servicio', 'hospedaje')
            contacto_val = request.POST.get('contacto_servicio', '')
            pagos_lista = request.POST.getlist('tipo_pago')
            pagos_str = ','.join(pagos_lista) if pagos_lista else 'efectivo'
            if hasattr(punto, 'servicio'):
                punto.servicio.tipo_servicio = tipo_servicio_val
                punto.servicio.contacto = contacto_val
                punto.servicio.tipo_pago = pagos_str
                punto.servicio.save()
            else:
                Servicio.objects.create(
                    id_punto=punto,
                    tipo_servicio=tipo_servicio_val,
                    contacto=contacto_val,
                    tipo_pago=pagos_str
                )

       # 3. Procesar nueva Galería Multimedia (Archivos locales)
        archivos_galeria = request.FILES.getlist('galeria_multimedia')
        if archivos_galeria:
            from django.core.files.storage import FileSystemStorage
            fs = FileSystemStorage()
            
            for f in archivos_galeria:
                ext = f.name.split('.')[-1].lower()
                tipo = 'imagen'
                if ext in ['mp4', 'avi', 'mov', 'webm']:
                    tipo = 'video'
                elif ext in ['mp3', 'wav', 'ogg']:
                    tipo = 'audio'
                
                # Guardar archivo físico y obtener la ruta pública
                filename = fs.save(f"galeria/{f.name}", f)
                url_publica = fs.url(filename)

                Galeria_Multimedia.objects.create(
                    id_punto=punto,
                    url_archivo=url_publica,
                    tipo_archivo=tipo,
                    descripcion=f"Subido el {timezone.now().date()}"
                )

        # 4. Eliminar fotos marcadas para borrar
        ids_eliminar = request.POST.getlist('galeria_eliminar')
        if ids_eliminar:
            Galeria_Multimedia.objects.filter(
                id_foto__in=ids_eliminar,
                id_punto=punto
            ).delete()

        return JsonResponse({'success': True, 'message': 'Punto guardado correctamente.'})

    except Exception as e:
        return JsonResponse({'success': False, 'error': f"Error interno: {str(e)}"}, status=500)



# --- VISTA PARA CREAR OFRENDA ---
def crear_ofrenda(request):
    if request.method == 'POST':
        # 1. Obtener datos del formulario
        nombre_punto = request.POST.get('nombre_punto', '').strip()
        anfitrion = request.POST.get('anfitrion', '').strip()
        
        # Opcional: Obtener latitud/longitud si tu formulario los tiene
        # lat = request.POST.get('latitud')
        # lon = request.POST.get('longitud')

        # 2. VALIDACIÓN: Verificar si ya existe el Punto de Interés (Case Insensitive)
        if Punto_Interes.objects.filter(nombre__iexact=nombre_punto).exists():
            messages.error(request, f"Ya existe un lugar registrado como '{nombre_punto}'.")
            return redirect('crear_ofrenda') # Cambia esto por el nombre de tu URL

        try:
            with transaction.atomic():
                # A) Buscar la categoría "Ofrenda" (ajusta el slug según tu BD)
                # Si no existe, podrías manejar el error o crearla al vuelo
                categoria_obj = Categoria_Sitio.objects.get(codigo_slug='ofrenda')

                # B) Crear primero el PADRE (Punto_Interes)
                nuevo_punto = Punto_Interes.objects.create(
                    nombre=nombre_punto.title(),
                    id_categoria=categoria_obj, # Asignamos la categoría
                    # latitud=lat,
                    # longitud=lon
                )

                # C) Crear el HIJO (Ofrenda) vinculándolo
                # Nota: Usamos 'id_punto' porque así llamaste a tu campo OneToOne
                Ofrenda.objects.create(
                    id_punto=nuevo_punto, 
                    anfitrion=anfitrion.title()
                )

            messages.success(request, f"Ofrenda '{nombre_punto.title()}' creada exitosamente.")

        except Categoria_Sitio.DoesNotExist:
            messages.error(request, "Error: No existe la categoría 'ofrenda' en la base de datos.")
        except Exception as e:
            messages.error(request, f"Ocurrió un error al guardar: {str(e)}")
            
    # Si no es POST, o si hubo error, redirige o renderiza
    return redirect('crear_ofrenda')


# --- VISTA PARA CREAR SERVICIO ---
def crear_servicio(request):
    if request.method == 'POST':
        # 1. Obtener datos
        nombre_punto = request.POST.get('nombre_punto', '').strip()
        tipo_servicio = request.POST.get('tipo_servicio')
        contacto = request.POST.get('contacto_servicio')
        
        # Para checkbox múltiples (tipo de pago), usamos getlist
        pagos_lista = request.POST.getlist('tipo_pago') 
        # Convertimos la lista ['efectivo', 'tarjeta'] a string "efectivo,tarjeta"
        pagos_str = ",".join(pagos_lista) if pagos_lista else "efectivo"

        # 2. VALIDACIÓN: Verificar duplicados
        if Punto_Interes.objects.filter(nombre__iexact=nombre_punto).exists():
            messages.error(request, f"Ya existe un lugar registrado como '{nombre_punto}'.")
            return redirect('crear_servicio')

        try:
            with transaction.atomic():
                # A) Buscar la categoría "Servicio" (ajusta el slug)
                categoria_obj = Categoria_Sitio.objects.get(codigo_slug='servicio')

                # B) Crear PADRE
                nuevo_punto = Punto_Interes.objects.create(
                    nombre=nombre_punto.title(),
                    id_categoria=categoria_obj
                )

                # C) Crear HIJO (Servicio)
                Servicio.objects.create(
                    id_punto=nuevo_punto,
                    tipo_servicio=tipo_servicio,
                    contacto=contacto,
                    tipo_pago=pagos_str
                )

            messages.success(request, f"Servicio '{nombre_punto.title()}' creado exitosamente.")

        except Categoria_Sitio.DoesNotExist:
            messages.error(request, "Error: No existe la categoría 'servicio' en la BD.")
        except Exception as e:
            messages.error(request, f"Error inesperado: {str(e)}")

    return redirect('crear_servicio')




    
def get_categorias_json(request):
    categorias = Categoria_Sitio.objects.values('id_categoria', 'nombre', 'codigo_slug')
    return JsonResponse(list(categorias), safe=False)

# --- VISTA PARA CREAR CATEGORÍA (MODAL) ---
@login_required
@require_POST
def crear_categoria(request):
    nombre = request.POST.get('nombre', '').strip()
    slug = request.POST.get('codigo_slug', '').strip()

    if not nombre or not slug:
        return JsonResponse({'status': 'error', 'message': 'Datos incompletos'})

    if Categoria_Sitio.objects.filter(nombre__iexact=nombre).exists():
        return JsonResponse({'status': 'error', 'message': 'Ya existe una categoría con ese nombre.'})

    if Categoria_Sitio.objects.filter(codigo_slug__iexact=slug).exists():
        return JsonResponse({'status': 'error', 'message': 'Ya existe una categoría con ese slug.'})

    nueva = Categoria_Sitio.objects.create(
        nombre=nombre.title(),
        codigo_slug=slug.lower()
    )

    return JsonResponse({
        'status': 'success',
        'new_id': nueva.id_categoria,
        'new_name': nueva.nombre,
        'new_slug': nueva.codigo_slug,
        'message': 'Categoría creada correctamente.'
    })

@login_required
@require_POST
def eliminar_categoria(request, categoria_id):
    try:
        categoria = get_object_or_404(Categoria_Sitio, id_categoria=categoria_id)

        if Sitio_turistico.objects.filter(id_categoria=categoria).exists():
            return JsonResponse({
                'status': 'error',
                'message': 'No se puede eliminar esta categoría porque está asignada a uno o más sitios turísticos.'
            }, status=400)

        categoria.delete()
        return JsonResponse({
            'status': 'success',
            'message': 'Categoría eliminada correctamente.'
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': f'Error al eliminar la categoría: {str(e)}'}, status=500)
    
    
    
    
@login_required
@require_POST 
def procesar_archivo(request, archivo_id):
    try:
        archivo = get_object_or_404(ArchivoKMZ, id_archivo=archivo_id, usuario=request.user)
        processor = KMLProcessor(archivo)
        resultado = processor.procesar()
        
        if resultado['success']:
            return JsonResponse(resultado)
        else:
            # Enviamos un 400 (Bad Request) en lugar de un 500
            return JsonResponse(resultado, status=400)
            
    except Exception as e:
        # Esto evita que el servidor "truene" con un 500
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@login_required
def actualizar_desde_url(request, archivo_id):
    """Actualiza un recurso desde su URL (verifica cambios)"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Método no permitido'}, status=405)
    
    try:
        archivo = get_object_or_404(ArchivoKMZ, id_archivo=archivo_id, usuario=request.user)
        
        # Verificar URL
        try:
            req = urllib.request.Request(archivo.archivo_path, method='HEAD')
            with urllib.request.urlopen(req, timeout=10) as response:
                archivo.codigo_respuesta_url = response.getcode()
                archivo.url_disponible = response.getcode() == 200
                archivo.ultima_verificacion_url = timezone.now()
                
                # Verificar si cambió el tamaño
                nuevo_tamanio = response.headers.get('Content-Length')
                if nuevo_tamanio and nuevo_tamanio != str(archivo.tamanio):
                    archivo.tamanio = int(nuevo_tamanio)
                
                archivo.save()
                
                # Si es KML/KMZ y está procesado, verificar si hay cambios
                if archivo.tipo_archivo in ['kml', 'kmz'] and archivo.procesado:
                    # Aquí podrías comparar hash si está calculado
                    if archivo.hash_archivo:
                        try:
                            # Recalcular hash
                            req = urllib.request.Request(archivo.archivo_path)
                            with urllib.request.urlopen(req, timeout=30) as response:
                                hash_obj = hashlib.sha256()
                                downloaded = 0
                                max_size = 1024 * 1024
                                
                                while True:
                                    chunk = response.read(8192)
                                    if not chunk:
                                        break
                                    hash_obj.update(chunk)
                                    downloaded += len(chunk)
                                    if downloaded >= max_size:
                                        break
                                
                                nuevo_hash = hash_obj.hexdigest()
                                
                                if nuevo_hash != archivo.hash_archivo:
                                    # Hash diferente, archivo cambió
                                    return JsonResponse({
                                        'success': True,
                                        'message': 'URL verificada. El archivo ha cambiado. ¿Deseas reprocesarlo?',
                                        'cambiado': True,
                                        'url_disponible': archivo.url_disponible
                                    })
                        except Exception:
                            pass
                
                return JsonResponse({
                    'success': True,
                    'message': 'URL verificada exitosamente',
                    'cambiado': False,
                    'url_disponible': archivo.url_disponible
                })
                
        except Exception as e:
            archivo.url_disponible = False
            archivo.ultima_verificacion_url = timezone.now()
            archivo.save()
            
            return JsonResponse({
                'success': False, 
                'error': f'No se pudo acceder a la URL: {str(e)}'
            }, status=400)
            
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)



@login_required
@require_POST
def eliminar_archivo(request, archivo_id):
    try:
        # 1. Busca en el modelo correcto: ArchivoKMZ
        # 2. Usa el campo clave correcto: id_archivo
        archivo = get_object_or_404(ArchivoKMZ, id_archivo=archivo_id, usuario=request.user)
        
        nombre = archivo.nombre_archivo
        
        # Como tienes on_delete=models.CASCADE en tus relaciones,
        # al borrar el archivo, se borrarán automáticamente las geometrías y puntos.
        archivo.delete()
        
        return JsonResponse({'success': True, 'message': f'Archivo "{nombre}" eliminado.'})
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': f'Error al eliminar: {str(e)}'}, status=400)

@login_required
def verificar_urls(request):
    """Verifica todas las URLs de los recursos del usuario"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Método no permitido'}, status=405)
    
    try:
        archivos = ArchivoKMZ.objects.filter(usuario=request.user)
        total = archivos.count()
        verificados = 0
        disponibles = 0
        no_disponibles = 0
        
        for archivo in archivos:
            try:
                req = urllib.request.Request(archivo.archivo_path, method='HEAD')
                with urllib.request.urlopen(req, timeout=5) as response:
                    archivo.codigo_respuesta_url = response.getcode()
                    archivo.url_disponible = response.getcode() == 200
                    archivo.ultima_verificacion_url = timezone.now()
                    archivo.save()
                    
                    if archivo.url_disponible:
                        disponibles += 1
                    else:
                        no_disponibles += 1
                        
            except Exception:
                archivo.url_disponible = False
                archivo.ultima_verificacion_url = timezone.now()
                archivo.save()
                no_disponibles += 1
            
            verificados += 1
        
        return JsonResponse({
            'success': True,
            'message': f'Verificación completada: {disponibles} disponibles, {no_disponibles} no disponibles',
            'total': total,
            'verificados': verificados,
            'disponibles': disponibles,
            'no_disponibles': no_disponibles
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


def vista_graficas(request):
    return render(request, 'myapp/charts.html')




@login_required
def redirigir_por_tipo_usuario(request):  
    """  
    Vista que redirige a los usuarios según su tipo después del login  
    """  
    try:  
        usuario = Usuario.objects.get(nombre_usuario=request.user.nombre_usuario)  
          
        if usuario.tipo == 'encuestador':  
            return redirect('encuestador_dashboard')  
        elif usuario.tipo == 'admin':  
            return redirect('lista_registros')  
        elif usuario.tipo == 'propietario':  
            return redirect('mis_propiedades')  
        else:  
            return redirect('vista_inicio')  
              
    except Usuario.DoesNotExist:  
        return redirect('login')
    

# =====================================================
# SISTEMA DE RESEÑAS GLOBALES DEL MUNICIPIO
# =====================================================

def _obtener_ip(request):
    """Extrae la IP real del visitante considerando proxies."""
    x_forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded:
        return x_forwarded.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', '0.0.0.0')


def _verificar_recaptcha(token):
    """Verifica el token reCAPTCHA con la API de Google."""
    import urllib.request as urlreq
    secret = settings.RECAPTCHA_SECRET_KEY
    url = 'https://www.google.com/recaptcha/api/siteverify'
    datos = urllib.parse.urlencode({
        'secret': secret,
        'response': token
    }).encode('utf-8')
    try:
        req = urlreq.Request(url, data=datos, method='POST')
        with urlreq.urlopen(req, timeout=5) as resp:
            resultado = json.loads(resp.read().decode('utf-8'))
        return resultado.get('success', False)
    except Exception:
        return False


@require_http_methods(['GET', 'POST'])
def api_resenas_globales(request):
    """
    GET  /api/resenas/  → Lista de reseñas aprobadas + estadísticas
    POST /api/resenas/  → Crear nueva reseña (calificacion + comentario, apodo opcional)
    """
    if request.method == 'GET':
        resenas_qs = ResenaGlobal.objects.filter(estado='aprobada')

        total = resenas_qs.count()
        promedio = 0.0
        distribucion = {'5': 0, '4': 0, '3': 0, '2': 0, '1': 0}

        if total > 0:
            from django.db.models import Avg
            avg = resenas_qs.aggregate(Avg('calificacion'))['calificacion__avg']
            promedio = round(float(avg), 1)
            for i in range(1, 6):
                distribucion[str(i)] = resenas_qs.filter(calificacion=i).count()

        resenas_list = []
        for r in resenas_qs[:50]:   # Máx. 50 por carga
            resenas_list.append({
                'id': r.id_resena,
                'autor': r.autor,
                'calificacion': r.calificacion,
                'comentario': r.comentario or '',
                'fecha': r.fecha_publicacion.strftime('%d %b %Y'),
                'likes': r.likes,
            })

        return JsonResponse({
            'promedio': promedio,
            'total': total,
            'distribucion': distribucion,
            'resenas': resenas_list,
        })
    #post
    try:
        datos = json.loads(request.body)
    except (json.JSONDecodeError, Exception):
        return JsonResponse({'error': 'JSON inválido'}, status=400)

    nombre_visitante = (datos.get('nombre_visitante') or '').strip()
    comentario       = (datos.get('comentario') or '').strip()
    calificacion     = datos.get('calificacion')
    recaptcha_token  = datos.get('recaptcha_token', '')

    if not nombre_visitante:
        nombre_visitante = 'Visitante'
    if len(nombre_visitante) > 50:
        return JsonResponse({'error': 'El apodo es demasiado largo (máx. 50 car.).'}, status=400)
    try:
        calificacion = int(calificacion)
        if not (1 <= calificacion <= 5):
            raise ValueError
    except (TypeError, ValueError):
        return JsonResponse({'error': 'Calificación inválida (1-5).'}, status=400)

    # Verificar reCAPTCHA
    if not _verificar_recaptcha(recaptcha_token):
        return JsonResponse({'error': 'Verifica que no eres un robot.'}, status=400)

    ip = _obtener_ip(request)
    hace_24h = tz.now() - timedelta(hours=24)
    resenas_ip = ResenaGlobal.objects.filter(
        ip_visitante=ip, fecha_publicacion__gte=hace_24h
    ).count()

    
    if resenas_ip >= 1:
       return JsonResponse(
            {'error': 'Límite alcanzado: máx. 3 reseñas por día desde la misma IP.'},
            status=429
        )
    estado_calculado = 'aprobada'
    texto_a_evaluar = f"{nombre_visitante} {comentario}".strip()
    result = {'label': None, 'score': 0.0}

    if texto_a_evaluar:
        try:
            app_conf = apps.get_app_config('myapp')
            classify = getattr(app_conf, 'classify_review', None)
            if callable(classify):
                result = classify(texto_a_evaluar) or result
                estado_calculado = result.get('estado', 'pendiente')
            else:
                # Fallback simple por palabras prohibidas
                palabras_prohibidas = ['puto', 'mierda', 'pendejo', 'idiota']
                if any(palabra in texto_a_evaluar.lower() for palabra in palabras_prohibidas):
                    estado_calculado = 'pendiente'
        except Exception as e:
            print(f"Error en Machine Learning: {e}")
            estado_calculado = 'pendiente'

    # Guardamos la reseña
    resena = ResenaGlobal.objects.create(
        id_usuario=request.user if request.user.is_authenticated else None,
        nombre_visitante=nombre_visitante,
        calificacion=calificacion,
        comentario=comentario or None,
        estado=estado_calculado, 
        modelo_label=result.get('label'),
        modelo_score=result.get('score'),
        ip_visitante=ip,
    )

    # Preparamos el mensaje de respuesta para el usuario
    mensaje = '¡Gracias! Tu reseña ha sido publicada.'
    if estado_calculado == 'pendiente':
        mensaje = '¡Gracias! Tu reseña fue recibida y está pendiente de moderación.'

    return JsonResponse({
        'ok': True,
        'mensaje': mensaje, # Enviamos el mensaje al Frontend
        'resena': {
            'id': resena.id_resena,
            'autor': resena.autor,
            'calificacion': resena.calificacion,
            'comentario': resena.comentario or '',
            'fecha': resena.fecha_publicacion.strftime('%d %b %Y'),
            'likes': 0,
        }
    }, status=201)


@require_http_methods(['POST'])
def like_resena(request, resena_id):
    """Incrementa el contador de likes de una reseña."""
    resena = get_object_or_404(ResenaGlobal, pk=resena_id, estado='aprobada')
    ResenaGlobal.objects.filter(pk=resena_id).update(likes=resena.likes + 1)
    return JsonResponse({'ok': True, 'likes': resena.likes + 1})


@require_http_methods(['POST'])
def reportar_resena(request, resena_id):
    """Marca la reseña como pendiente para revisión del admin."""
    resena = get_object_or_404(ResenaGlobal, pk=resena_id)
    resena.estado = 'pendiente'
    resena.save(update_fields=['estado'])
    return JsonResponse({'ok': True, 'mensaje': 'Reseña reportada. Gracias por tu aviso.'})


# =====================================================
# GESTI�N DE RESE�AS � PANEL ADMINISTRATIVO
# =====================================================

from django.contrib.auth.decorators import login_required

@login_required
def gestionar_resenas(request):
    resenas = ResenaGlobal.objects.all().order_by('-fecha_publicacion')
    context = {
        'resenas': resenas,
        'resenas_aprobadas': resenas.filter(estado='aprobada').count(),
        'resenas_pendientes': resenas.filter(estado='pendiente').count(),
        'resenas_ocultas': resenas.filter(estado='oculta').count(),
    }
    return render(request, 'myapp/mod_db/crud_resenas.html', context)

@login_required
@require_http_methods(['POST'])
def cambiar_estado_resena(request, resena_id):
    import json as _json
    resena = get_object_or_404(ResenaGlobal, pk=resena_id)
    try:
        datos = _json.loads(request.body)
        nuevo_estado = datos.get('estado', '')
    except Exception:
        return JsonResponse({'error': 'JSON invalido'}, status=400)
    if nuevo_estado not in {'aprobada', 'pendiente', 'oculta'}:
        return JsonResponse({'error': 'Estado no valido'}, status=400)
    resena.estado = nuevo_estado
    resena.save(update_fields=['estado'])
    return JsonResponse({'ok': True, 'estado': nuevo_estado})

@login_required
@require_http_methods(['POST'])
def eliminar_resena_admin(request, resena_id):
    resena = get_object_or_404(ResenaGlobal, pk=resena_id)
    resena.delete()
    return JsonResponse({'ok': True})

@login_required
@require_http_methods(['POST'])
def accion_masiva_resenas(request):
    import json as _json
    try:
        datos = _json.loads(request.body)
        ids = [int(i) for i in datos.get('ids', [])]
        estado = datos.get('estado', '')
        accion = datos.get('accion', '')
    except Exception:
        return JsonResponse({'error': 'Datos invalidos'}, status=400)
    if not ids:
        return JsonResponse({'error': 'Sin IDs'}, status=400)
    qs = ResenaGlobal.objects.filter(pk__in=ids)
    if accion == 'eliminar':
        count = qs.count()
        qs.delete()
        return JsonResponse({'ok': True, 'eliminadas': count})
    if estado not in {'aprobada', 'pendiente', 'oculta'}:
        return JsonResponse({'error': 'Estado no valido'}, status=400)
    actualizadas = qs.update(estado=estado)
    return JsonResponse({'ok': True, 'actualizadas': actualizadas})

# ==========================================
# GESTIÓN DE USUARIOS (CRUD)
# ==========================================

@login_required
def lista_usuarios(request):
    if request.user.tipo != 'admin':
        return HttpResponseForbidden("Acceso denegado. Solo administradores.")
    
    # Excluir usuarios inactivos
    usuarios = Usuario.objects.filter(is_active=True).order_by('-fecha_registro')
    # Puntos para el selector múltiple de propietarios
    puntos = Punto_Interes.objects.filter(estado='activo').order_by('nombre')
    
    context = {
        'usuarios': usuarios,
        'puntos': puntos
    }
    return render(request, 'myapp/lista_usuarios.html', context)

@login_required
@require_http_methods(["POST"])
@transaction.atomic
def crear_usuario(request):
    if request.user.tipo != 'admin':
        return JsonResponse({'error': 'Acceso denegado.'}, status=403)
        
    try:
        nombre_usuario = request.POST.get('nombre_usuario')
        nombre = request.POST.get('nombre')
        ap = request.POST.get('ap')
        am = request.POST.get('am', '')
        email = request.POST.get('email')
        password = request.POST.get('password')
        tipo = request.POST.get('tipo')
        
        if not all([nombre_usuario, nombre, ap, email, password, tipo]):
            return JsonResponse({'error': 'Todos los campos obligatorios deben ser llenados'}, status=400)
            
        if Usuario.objects.filter(nombre_usuario=nombre_usuario).exists():
            return JsonResponse({'error': 'El nombre de usuario ya existe'}, status=400)
            
        if Usuario.objects.filter(email=email).exists():
            return JsonResponse({'error': 'El correo ya está registrado'}, status=400)
            
        if tipo not in ['admin', 'encuestador', 'propietario']:
            return JsonResponse({'error': 'Tipo de usuario inválido'}, status=400)
            
        usuario = Usuario.objects.create_user(
            nombre_usuario=nombre_usuario,
            email=email,
            password=password,
            nombre=nombre,
            ap=ap,
            am=am,
            tipo=tipo
        )
        
        # Create related profile
        if tipo == 'admin':
            Administrador.objects.create(id_usuario=usuario)
        elif tipo == 'encuestador':
            Encuestador.objects.create(id_usuario=usuario)
        elif tipo == 'propietario':
            tipo_propiedad = request.POST.get('tipo_propiedad')
            tipo_comercio = request.POST.get('tipo_comercio') if tipo_propiedad == 'comercio' else None
            propietario = Propietario.objects.create(
                id_usuario=usuario,
                tipo_propiedad=tipo_propiedad,
                tipo_comercio=tipo_comercio
            )
            
            puntos_asignados = request.POST.getlist('puntos_asignados')
            if puntos_asignados:
                puntos_objs = Punto_Interes.objects.filter(id_punto__in=puntos_asignados)
                for p in puntos_objs:
                    p.propietarios.add(propietario)
            
        return JsonResponse({'success': True, 'message': 'Usuario creado exitosamente.'})
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
@require_http_methods(["POST"])
@transaction.atomic
def editar_usuario(request, id_usuario):
    if request.user.tipo != 'admin':
        return JsonResponse({'error': 'Acceso denegado.'}, status=403)
        
    try:
        usuario = get_object_or_404(Usuario, id_usuario=id_usuario)
        
        nombre = request.POST.get('nombre')
        ap = request.POST.get('ap')
        am = request.POST.get('am', '')
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        if not all([nombre, ap, email]):
            return JsonResponse({'error': 'Nombre, apellidos y correo son obligatorios'}, status=400)
            
        # Check email uniqueness except for current user
        if Usuario.objects.filter(email=email).exclude(id_usuario=id_usuario).exists():
            return JsonResponse({'error': 'El correo ya está registrado por otro usuario'}, status=400)
            
        usuario.nombre = nombre
        usuario.ap = ap
        usuario.am = am
        usuario.email = email
        
        # Guardar cambios extras si el usuario es Propietario
        if usuario.tipo == 'propietario':
            if hasattr(usuario, 'propietario'):
                tipo_propiedad = request.POST.get('tipo_propiedad')
                tipo_comercio = request.POST.get('tipo_comercio') if tipo_propiedad == 'comercio' else None
                usuario.propietario.tipo_propiedad = tipo_propiedad
                usuario.propietario.tipo_comercio = tipo_comercio
                usuario.propietario.save()
                
                puntos_asignados = request.POST.getlist('puntos_asignados')
                if puntos_asignados is not None:
                    # Limpiamos puntos actuales y añadimos los nuevos
                    usuario.propietario.puntos_asignados.clear()
                    if puntos_asignados:
                        puntos_objs = Punto_Interes.objects.filter(id_punto__in=puntos_asignados)
                        for p in puntos_objs:
                            p.propietarios.add(usuario.propietario)
        
        # Solo actualiza la contraseña si se proporcionó una nueva
        if password and len(password.strip()) > 0:
            usuario.set_password(password)
            
        usuario.save()
        return JsonResponse({'success': True, 'message': 'Usuario actualizado exitosamente.'})
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
@require_http_methods(["POST"])
@transaction.atomic
def eliminar_usuario(request, id_usuario):
    if request.user.tipo != 'admin':
        return JsonResponse({'error': 'Acceso denegado.'}, status=403)
        
    try:
        usuario = get_object_or_404(Usuario, id_usuario=id_usuario)
        
        # Don't allow deleting oneself
        if usuario.id_usuario == request.user.id_usuario:
            return JsonResponse({'error': 'No puedes eliminar tu propio usuario'}, status=400)
            
        # Soft delete (Desactivación)
        usuario.is_active = False
        usuario.save()
        
        return JsonResponse({'success': True, 'message': 'Usuario desactivado exitosamente.'})
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

# ==========================================
# 8. VISTAS DEL PROPIETARIO
# ==========================================

@login_required
def mis_propiedades(request):
    if request.user.tipo != 'propietario':
        return HttpResponseForbidden("Acceso denegado. Solo propietarios.")
    
    try:
        propietario = request.user.propietario
        puntos = propietario.puntos_asignados.all()
    except Exception:
        puntos = []
        
    context = {
        'puntos': puntos
    }
    return render(request, 'myapp/mis_propiedades.html', context)

@login_required
@require_POST
def editar_mi_propiedad(request, id_punto):
    if request.user.tipo != 'propietario':
        return JsonResponse({'success': False, 'error': 'Acceso denegado.'}, status=403)
        
    try:
        propietario = request.user.propietario
        punto = get_object_or_404(Punto_Interes, id_punto=id_punto, propietarios=propietario)
        
        # 1. Campos básicos permitidos
        punto.nombre = request.POST.get('nombre_punto', punto.nombre)
        punto.descripcion = request.POST.get('descripcion', '')
        if 'imagen_portada' in request.FILES and request.FILES['imagen_portada']:
            from django.core.files.storage import FileSystemStorage
            fs = FileSystemStorage()
            f_port = request.FILES['imagen_portada']
            filename_port = fs.save(f"portadas/{f_port.name}", f_port)
            punto.imagen_portada = fs.url(filename_port)
                
        fecha_inicio = request.POST.get('fecha_inicio')
        punto.fecha_inicio = fecha_inicio if fecha_inicio else None

        fecha_fin = request.POST.get('fecha_fin')
        punto.fecha_fin = fecha_fin if fecha_fin else None

        hora_apertura = request.POST.get('hora_apertura')
        punto.hora_apertura = hora_apertura if hora_apertura else None

        hora_cierre = request.POST.get('hora_cierre')
        punto.hora_cierre = hora_cierre if hora_cierre else None

        dias_seleccionados = request.POST.getlist('dias_semana')
        punto.dias_semana_list = dias_seleccionados
        punto.save()
        
        # 2. Submodelos según categoría
        categoria = punto.categoria
        if categoria == 'ofrenda':
            anfitrion = request.POST.get('anfitrion', '').strip()
            if hasattr(punto, 'ofrenda'):
                punto.ofrenda.anfitrion = anfitrion
                punto.ofrenda.save()
            else:
                Ofrenda.objects.create(id_punto=punto, anfitrion=anfitrion)
                
        elif categoria == 'servicio':
            tipo_servicio_val = request.POST.get('tipo_servicio', 'hospedaje')
            contacto = request.POST.get('contacto', '')
            tipo_pagos_sel = request.POST.getlist('tipo_pago')
            str_pagos = ",".join(tipo_pagos_sel) if tipo_pagos_sel else 'efectivo'
            
            if hasattr(punto, 'servicio'):
                punto.servicio.tipo_servicio = tipo_servicio_val
                punto.servicio.contacto = contacto
                punto.servicio.tipo_pago = str_pagos
                punto.servicio.save()
            else:
                Servicio.objects.create(
                    id_punto=punto,
                    tipo_servicio=tipo_servicio_val,
                    contacto=contacto,
                    tipo_pago=str_pagos
                )
                
        # Propietario no puede editar geometría ni borrar
        archivos_galeria = request.FILES.getlist('galeria_multimedia')
        if archivos_galeria:
            from django.core.files.storage import FileSystemStorage
            fs = FileSystemStorage()
            for f in archivos_galeria:
                ext = f.name.split('.')[-1].lower()
                tipo = 'video' if ext in ['mp4', 'avi', 'mov', 'webm'] else 'audio' if ext in ['mp3', 'wav'] else 'imagen'
                
                filename = fs.save(f"galeria/{f.name}", f)
                url_publica = fs.url(filename)
                Galeria_Multimedia.objects.create(
                    id_punto=punto,
                    url_archivo=url_publica,
                    tipo_archivo=tipo,
                    descripcion=f"Subido por propietario el {timezone.now().date()}"
                )

        # 4. Eliminar fotos marcadas para borrar
        ids_eliminar = request.POST.getlist('galeria_eliminar')
        if ids_eliminar:
            Galeria_Multimedia.objects.filter(id_foto__in=ids_eliminar, id_punto=punto).delete()
        
        return JsonResponse({'success': True, 'message': 'Propiedad actualizada exitosamente.'})
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)






# Reglas estrictas para el chatbot de Huaquechula
INSTRUCCIONES_SISTEMA = """
Eres el asistente virtual oficial del 'Observatorio de Datos Huaquechula'. 
Tu objetivo es ayudar a los turistas a entender el mapa, encontrar ofrendas, sitios turísticos y servicios.
REGLA ESTRICTA 1: Solo puedes hablar sobre temas relacionados con turismo, Huaquechula, las ofrendas o tradiciones locales.
REGLA ESTRICTA 2: Si el usuario te pregunta sobre otros temas, debes responder educadamente: "Lo siento, solo puedo ayudarte con información sobre el recorrido turístico del municipio."
Sé amable y conciso.
"""

@csrf_exempt
def chatbot_api(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)

    try:
        data = json.loads(request.body)
        pregunta_usuario = data.get('pregunta', '')

        # llave
        API_KEY = os.getenv('GROQ_API_KEY')
        
        # Endpoint compatible con OpenAI que usa Groq
        url = "https://api.groq.com/openai/v1/chat/completions"

        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {API_KEY}'
        }

        # Payload formato Groq/OpenAI
        payload = {
            "model": "llama-3.1-8b-instant",  # El nombre exacto sacado de tu consola
            "messages": [
                {
                    "role": "system",
                    "content": INSTRUCCIONES_SISTEMA
                },
                {
                    "role": "user",
                    "content": pregunta_usuario
                }
            ]
        }

        respuesta_http = requests.post(url, headers=headers, json=payload, timeout=15)

        if respuesta_http.status_code == 200:
            datos = respuesta_http.json()
            texto_respuesta = datos['choices'][0]['message']['content']
            return JsonResponse({'respuesta': texto_respuesta})
            
        else:
            print(f"[CHATBOT ERROR] Status: {respuesta_http.status_code}")
            print(f"[CHATBOT ERROR] Body: {respuesta_http.text}")
            return JsonResponse({'respuesta': 'El asistente no está disponible en este momento. Intenta más tarde.'})

    except Exception as e:
        print(f"[CHATBOT ERROR CRÍTICO] {e}")
        return JsonResponse({'respuesta': 'Error interno del servidor.'})

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
        usuario = Usuario.objects.get(nombre_usuario=request.user.nombre_usuario)    
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
        usuario = Usuario.objects.get(nombre_usuario=request.user.nombre_usuario)  
          
        if usuario.tipo == 'encuestador':  
            return redirect('encuestador_dashboard')  
        elif usuario.tipo == 'admin':  
            return redirect('lista_registros')  
        elif usuario.tipo == 'propietario':  
            return redirect('mis_propiedades')  
        else:  
            return redirect('vista_inicio')  
              
    except Usuario.DoesNotExist:  
        return redirect('login')
    

# views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse, FileResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
# Repository functionality - Models not yet implemented
# from .models import Documento, Categoria


def repositorio(request):
    """Vista principal del repositorio - ahora usa repositorio_galeria_prueba.html con carrusel dinámico"""
    import os
    from django.conf import settings
    
    tipo_filtro = request.GET.get('tipo', '')
    busqueda = request.GET.get('q', '')
    
    # Filtrar documentos que son públicos
    documentos = Documento.objects.filter(es_publico=True)
    
    if tipo_filtro:
        documentos = documentos.filter(tipo=tipo_filtro)
        
    if busqueda:
        documentos = documentos.filter(
            Q(titulo__icontains=busqueda) | 
            Q(descripcion__icontains=busqueda)
        )
        
    # Calcular estadísticas de tipos
    stats_tipos = {
        'videos': Documento.objects.filter(es_publico=True, tipo='video').count(),
        'historicos': Documento.objects.filter(es_publico=True, tipo='historico').count(),
        'reportes': Documento.objects.filter(es_publico=True, tipo='reporte').count(),
    }
    
    # Paginación
    paginator = Paginator(documentos, 9)  # 9 documentos por página para la cuadrícula premium
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Cargar imágenes de la carpeta carrucel local en media
    carrucel_dir = os.path.join(settings.MEDIA_ROOT, 'carrucel')
    imagenes_carrucel = []
    if os.path.exists(carrucel_dir):
        try:
            for file in sorted(os.listdir(carrucel_dir)):
                if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp')):
                    imagenes_carrucel.append(f"{settings.MEDIA_URL}carrucel/{file}")
        except Exception:
            pass
            
    context = {
        'documentos': page_obj,
        'stats_tipos': stats_tipos,
        'tipos_choices': Documento._meta.get_field('tipo').choices,
        'tipo_filtro': tipo_filtro,
        'busqueda': busqueda,
        'imagenes_carrucel': imagenes_carrucel,
    }
    return render(request, 'myapp/repositorio_galeria_prueba.html', context)

def obtener_documentos_categoria(request, categoria_id):
    """API para obtener documentos de una categoría específica"""
    try:
        if categoria_id == 'all':
            documentos = Documento.objects.filter(es_publico=True)
        else:
            documentos = Documento.objects.filter(
                categoria_id=categoria_id,
                es_publico=True
            )
        
        documentos_data = []
        for doc in documentos:
            doc_url = doc.archivo.url if doc.archivo else (doc.url or "")
            icono = "fas fa-file-alt"
            if doc.tipo == 'video':
                icono = "fas fa-play-circle"
            elif doc.tipo == 'historico':
                icono = "fas fa-book-open"
            
            documentos_data.append({
                'id': doc.id,
                'titulo': doc.titulo,
                'descripcion': doc.descripcion or "",
                'url': doc_url,
                'tipo': doc.tipo_archivo or doc.tipo or "pdf",
                'tamaño': doc.tamaño_formateado() if hasattr(doc, 'tamaño_formateado') else f"{round(doc.tamaño/1024, 1)} KB",
                'fecha': doc.fecha_subida.strftime('%d/%m/%Y') if doc.fecha_subida else '',
                'icono': icono,
                'es_video': doc.tipo == 'video',
                'es_imagen': (doc.tipo_archivo or '').lower() in ['jpg', 'jpeg', 'png', 'gif'],
                'es_pdf': (doc.tipo_archivo or '').lower() == 'pdf' or doc.tipo == 'reporte',
            })
        
        return JsonResponse({'documentos': documentos_data})
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def dashboard_view(request):
    """
    Vista principal del Dashboard del Observatorio.
    Muestra los indicadores agrupados por Eje y Categoría,
    con datos de sparklines, tendencias y conteos para el dashboard premium.

    NOTA: Los atributos calculados (trend_percent, sparkline_values) se guardan
    en un dict 'indicators_data' porque el template re-evalúa categoria.indicadores.all()
    creando objetos Python frescos sin los atributos asignados en el bucle de la vista.
    """
    import json

    ejes = Eje.objects.prefetch_related('categorias__indicadores__mediciones').all()

    total_indicadores = 0
    total_categorias = 0
    indicators_data = {}  # {pk: {sparkline_values, trend_direction, trend_percent}}

    for eje in ejes:
        eje_indicator_count = 0
        for categoria in eje.categorias.all():
            total_categorias += 1
            for indicador in categoria.indicadores.all():
                eje_indicator_count += 1

                mediciones = list(indicador.mediciones.all().order_by('periodo'))
                values = [float(m.valor) for m in mediciones]

                sparkline = json.dumps(values) if len(values) > 1 else ''
                trend_direction = 'stable'
                trend_percent = '0.0'

                if len(values) >= 2:
                    prev_val = values[-2]
                    last_val = values[-1]
                    if prev_val != 0:
                        change = ((last_val - prev_val) / abs(prev_val)) * 100
                        trend_percent = f"{abs(change):.1f}"
                        if change > 0.5:
                            trend_direction = 'up'
                        elif change < -0.5:
                            trend_direction = 'down'

                indicators_data[indicador.pk] = {
                    'sparkline_values': sparkline,
                    'trend_direction': trend_direction,
                    'trend_percent': trend_percent,
                }

        eje.indicator_count = eje_indicator_count
        total_indicadores += eje_indicator_count

    return render(request, 'myapp/dashboard.html', {
        'ejes': ejes,
        'total_indicadores': total_indicadores,
        'total_categorias': total_categorias,
        'indicators_data': indicators_data,
    })

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
        # Siempre inicializar para evitar que el template muestre el nombre de la variable
        indicador.trend_direction = 'stable'
        indicador.trend_percent = '0.0'
        indicador.sparkline_values = ''

        mediciones = list(indicador.mediciones.all().order_by('periodo'))
        values = [float(m.valor) for m in mediciones]

        if len(values) > 1:
            indicador.sparkline_values = json.dumps(values)

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
            
    return render(request, 'myapp/category_detail.html', {
        'categoria': categoria,
        'indicadores': indicadores,
        'eje': categoria.eje,
    })


# ============================================
# API de Estadísticas de Visitantes (Inicio)
# ============================================

@require_http_methods(["GET"])
def api_visitor_stats(request):
    """
    Agrega datos de RegistroVisita para las gráficas de la página de inicio.
    Devuelve:
      - total_visitantes, pct_extranjeros
      - visitantes_por_mes  (últimos 12 meses)
      - top_procedencias    (top 5 ciudades)
      - motivo_visita       (distribución)
      - transporte          (distribución)
      - genero_por_rango    (pirámide)
      - estancia_promedio
      - visitas_previas_promedio
    """
    from django.db.models import Sum, Count, Avg, Q
    from django.db.models.functions import TruncMonth
    from collections import defaultdict
    import calendar

    registros = RegistroVisita.objects.all()
    total = registros.count()

    if total == 0:
        return JsonResponse({
            'total_visitantes': 0,
            'pct_extranjeros': 0,
            'visitantes_por_mes': {'labels': [], 'values': []},
            'top_procedencias': {'labels': [], 'values': []},
            'motivo_visita': {'labels': [], 'values': []},
            'transporte': {'labels': [], 'values': []},
            'genero_por_rango': {'rangos': [], 'mujeres': [], 'hombres': []},
            'estancia_promedio': 0,
            'visitas_previas_promedio': 0,
        })

    # Total personas (sumando campos de edad/género)
    total_personas_agg = registros.aggregate(
        tot_m=Sum('mujeres_0_15') + Sum('mujeres_16_30') + Sum('mujeres_31_45') +
              Sum('mujeres_46_60') + Sum('mujeres_61_75') + Sum('mujeres_76_mas') +
              Sum('hombres_0_15') + Sum('hombres_16_30') + Sum('hombres_31_45') +
              Sum('hombres_46_60') + Sum('hombres_61_75') + Sum('hombres_76_mas'),
    )
    total_personas = total_personas_agg['tot_m'] or 0

    # Extranjeros
    ext_count = registros.filter(es_extranjero=True).count()
    pct_ext = round(ext_count / total * 100, 1) if total else 0

    # Visitantes por mes (últimos 12 meses)
    from datetime import date
    from dateutil.relativedelta import relativedelta
    hoy = date.today()
    meses_labels, meses_values = [], []
    MESES_ES = ['Ene','Feb','Mar','Abr','May','Jun','Jul','Ago','Sep','Oct','Nov','Dic']
    for i in range(11, -1, -1):
        d = hoy - relativedelta(months=i)
        qs = registros.filter(fecha__year=d.year, fecha__month=d.month)
        total_mes = 0
        for r in qs:
            total_mes += r.total_personas
        meses_labels.append(f"{MESES_ES[d.month - 1]} {d.year}")
        meses_values.append(total_mes)

    # Top procedencias
    proc_counts = defaultdict(int)
    for r in registros:
        proc_counts[r.procedencia.strip().title()] += r.total_personas
    top_proc = sorted(proc_counts.items(), key=lambda x: x[1], reverse=True)[:6]
    top_labels = [p[0] for p in top_proc]
    top_values = [p[1] for p in top_proc]

    # Motivo de visita
    motivos_raw = registros.values('motivo_visita').annotate(cnt=Count('id_registro')).order_by('-cnt')
    MOTIVO_MAP = {'turismo': 'Turismo', 'negocios': 'Negocios', 'visita_familiar': 'Visita Familiar',
                  'estudios': 'Estudios', 'otros': 'Otros'}
    motivo_labels = [MOTIVO_MAP.get(m['motivo_visita'], m['motivo_visita']) for m in motivos_raw]
    motivo_values = [m['cnt'] for m in motivos_raw]

    # Transporte
    trans_raw = registros.values('tipo_transporte').annotate(cnt=Count('id_registro')).order_by('-cnt')
    TRANS_MAP = {'automovil': 'Automóvil', 'autobus': 'Autobús', 'avion': 'Avión',
                 'tren': 'Tren', 'otros': 'Otros'}
    trans_labels = [TRANS_MAP.get(t['tipo_transporte'], t['tipo_transporte']) for t in trans_raw]
    trans_values = [t['cnt'] for t in trans_raw]

    # Pirámide por rango de edad
    rangos = ['0-15', '16-30', '31-45', '46-60', '61-75', '76+']
    campos_m = ['mujeres_0_15','mujeres_16_30','mujeres_31_45','mujeres_46_60','mujeres_61_75','mujeres_76_mas']
    campos_h = ['hombres_0_15','hombres_16_30','hombres_31_45','hombres_46_60','hombres_61_75','hombres_76_mas']
    mujeres_vals = [registros.aggregate(t=Sum(c))['t'] or 0 for c in campos_m]
    hombres_vals = [registros.aggregate(t=Sum(c))['t'] or 0 for c in campos_h]

    # Promedios
    avg_estancia = round(registros.aggregate(a=Avg('estancia_dias'))['a'] or 0, 1)
    avg_visitas = round(registros.aggregate(a=Avg('visitas_previas'))['a'] or 0, 1)

    # Visitantes anuales (año en curso)
    visitantes_anuales = 0
    for r in registros.filter(fecha__year=hoy.year):
        visitantes_anuales += r.total_personas

    # Visitantes durante la tradición (Oct-Nov: Día de Muertos)
    visitantes_tradicion = 0
    for r in registros.filter(fecha__month__in=[10, 11]):
        visitantes_tradicion += r.total_personas

    # Satisfacción promedio de reseñas aprobadas
    from .models import ResenaGlobal
    resenas_qs = ResenaGlobal.objects.filter(estado='aprobada')
    satisfaccion_agg = resenas_qs.aggregate(avg=Avg('calificacion'))
    satisfaccion_promedio = round(satisfaccion_agg['avg'] or 0, 1)
    total_resenas = resenas_qs.count()

    return JsonResponse({
        'total_visitantes': total_personas,
        'total_registros': total,
        'pct_extranjeros': pct_ext,
        'visitantes_anuales': visitantes_anuales,
        'visitantes_tradicion': visitantes_tradicion,
        'satisfaccion_promedio': satisfaccion_promedio,
        'total_resenas': total_resenas,
        'visitantes_por_mes': {'labels': meses_labels, 'values': meses_values},
        'top_procedencias': {'labels': top_labels, 'values': top_values},
        'motivo_visita': {'labels': motivo_labels, 'values': motivo_values},
        'transporte': {'labels': trans_labels, 'values': trans_values},
        'genero_por_rango': {'rangos': rangos, 'mujeres': mujeres_vals, 'hombres': hombres_vals},
        'estancia_promedio': avg_estancia,
        'visitas_previas_promedio': avg_visitas,
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
    from django.db.models.functions import TruncDate
    try:
        usuario = Usuario.objects.get(nombre_usuario=request.user.nombre_usuario)
        if usuario.tipo not in ['encuestador', 'admin']:
            return HttpResponseForbidden("No tienes permiso para acceder al portal de encuestadores.")
    except Usuario.DoesNotExist:
        return HttpResponse('Usuario no encontrado.', status=404)

    # Obtener encuestador actual (si aplica)
    encuestador = None
    try:
        encuestador = Encuestador.objects.get(id_usuario=usuario)
    except Exception:
        pass

    # ── Totales globales ──
    total_registros = RegistroVisita.objects.count()
    total_residentes = EncuestaResidente.objects.count()
    total_comercio = EncuestaComercio.objects.count()
    total_encuestas = total_residentes + total_comercio

    # ── Propias (solo para encuestadores, no admin) ──
    mis_registros = 0
    mis_residentes = 0
    mis_comercio = 0
    if encuestador:
        mis_registros = RegistroVisita.objects.filter(clave_encuestador=encuestador).count()
        mis_residentes = EncuestaResidente.objects.filter(encuestador=encuestador).count()
        mis_comercio = EncuestaComercio.objects.filter(encuestador=encuestador).count()

    # ── Actividad reciente (últimos 7 días) ──
    hace_7_dias = timezone.now() - timedelta(days=7)
    registros_recientes = RegistroVisita.objects.filter(fecha__gte=hace_7_dias).count()
    encuestas_recientes = (
        EncuestaResidente.objects.filter(fecha__gte=hace_7_dias).count() +
        EncuestaComercio.objects.filter(fecha__gte=hace_7_dias).count()
    )

    # ── Distribución por motivo de visita ──
    motivos = (
        RegistroVisita.objects
        .values('motivo_visita')
        .annotate(total=Count('id_registro'))
        .order_by('-total')
    )

    # ── Últimos 5 registros ──
    ultimos_registros = RegistroVisita.objects.order_by('-fecha')[:5]

    context = {
        'usuario': usuario,
        'encuestador': encuestador,
        # Totales
        'total_registros': total_registros,
        'total_encuestas': total_encuestas,
        'total_residentes': total_residentes,
        'total_comercio': total_comercio,
        # Propias
        'mis_registros': mis_registros,
        'mis_residentes': mis_residentes,
        'mis_comercio': mis_comercio,
        # Recientes
        'registros_recientes': registros_recientes,
        'encuestas_recientes': encuestas_recientes,
        # Análisis
        'motivos': motivos,
        'ultimos_registros': ultimos_registros,
    }
    return render(request, 'myapp/encuestador_dashboard.html', context)

@login_required
def nueva_encuesta_residente(request):
    try:  
        usuario = Usuario.objects.get(nombre_usuario=request.user.nombre_usuario)  
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
def nueva_encuesta_comercio(request):
    try:  
        usuario = Usuario.objects.get(nombre_usuario=request.user.nombre_usuario)  
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
        form = EncuestaComercioForm(request.POST)
        if form.is_valid():
            encuesta = form.save(commit=False)
            encuesta.encuestador = encuestador
            encuesta.save()
            messages.success(request, 'Encuesta a comercio guardada exitosamente.')
            return redirect('encuestador_dashboard')
    else:
        form = EncuestaComercioForm()

    return render(request, 'myapp/form_comercio.html', {'form': form})


# ================================================================
# RECUPERACIÓN DE CONTRASEÑA — Vistas personalizadas
# ================================================================

from django.contrib.auth.views import (
    PasswordResetView,
    PasswordResetConfirmView,
)
from django.contrib.auth.forms import SetPasswordForm
from django.urls import reverse_lazy


class CustomPasswordResetView(PasswordResetView):
    """
    Vista de solicitud de recuperación de contraseña.
    Usa el modelo de usuario personalizado (Usuario) y busca por email.
    """
    template_name           = 'registration/password_reset.html'
    email_template_name     = 'registration/password_reset_email.html'
    html_email_template_name = 'registration/password_reset_email.html'
    subject_template_name   = 'registration/password_reset_subject.txt'
    success_url             = reverse_lazy('password_reset_done')

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Asegurarse de que se busque el email en el modelo correcto
        form.fields['email'].label = 'Correo electrónico'
        return form


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    """
    Vista de confirmación de nueva contraseña.
    Valida que la nueva contraseña sea diferente a la actual.
    """
    template_name = 'registration/password_reset_confirm.html'
    success_url   = reverse_lazy('password_reset_complete')

    def form_valid(self, form):
        """
        Antes de guardar, verifica que la nueva contraseña
        no sea idéntica a la contraseña actual del usuario.
        """
        nueva = form.cleaned_data.get('new_password1')
        usuario = self.user  # disponible porque PasswordResetConfirmView lo establece en dispatch()

        if usuario and usuario.check_password(nueva):
            form.add_error(
                'new_password2',
                'La nueva contraseña no puede ser igual a la contraseña anterior. '
                'Por favor, elige una contraseña diferente.'
            )
            return self.form_invalid(form)

        return super().form_valid(form)
