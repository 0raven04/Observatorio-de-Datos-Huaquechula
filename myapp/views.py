from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseForbidden, JsonResponse, FileResponse
from pytz import timezone
from myapp.models import (
    ArchivoKMZ, GeometriaEspacial, Punto_Interes, Categoria_Sitio, Galeria_Multimedia, Servicio, Ofrenda, Documento, Administrador, Sitio_turistico, Usuario, Encuestador, RegistroVisita
)
from django.utils import timezone
from django.contrib.auth.hashers import make_password
from django.db import IntegrityError, transaction
from django.contrib.auth import logout
from django.contrib import messages
import subprocess
from django.conf import settings
from datetime import datetime
import os
import sys

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
                clave_encuestador=usuario.id_usuario,
                defaults={
                    'id_usuario': usuario,
                    'fecha_registro': timezone.now()
                }  
            )  
    except (Usuario.DoesNotExist, Encuestador.DoesNotExist):  
        return HttpResponse('Usuario no encontrado.', status=404)

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
    
    

@login_required  
@transaction.atomic  
def formulario(request):  
    """  
    Vista específica para que encuestadores puedan crear registros  
    """
    try:  
        usuario = Usuario.objects.get(nombre_usuario=request.user.nombre_usuario)  
        if usuario.tipo != 'encuestador':  
            return HttpResponseForbidden("No tienes permiso. Solo los encuestadores pueden acceder.")  
          
        encuestador = Encuestador.objects.get(id_usuario=usuario)  
    except (Usuario.DoesNotExist, Encuestador.DoesNotExist):  
        return HttpResponse('Encuestador no encontrado.', status=404)  
  
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
    clasificacion = request.GET.get('clasificacion', '')
    tipo_filtro = request.GET.get('tipo', '')  # NUEVO: Capturar filtro de tipo
    sort_by = request.GET.get('sort', 'fecha_carga')
    order = request.GET.get('order', 'desc')
    search = request.GET.get('search', '')
    
    # Base queryset
    documentos = Documento.objects.all()
    
    # Aplicar filtro por clasificación
    if clasificacion in dict(Documento.CLASIFICACION_CHOICES):
        documentos = documentos.filter(clasificacion=clasificacion)

    # NUEVO: Aplicar filtro por tipo
    if tipo_filtro in dict(Documento.TIPO_CHOICES):
        documentos = documentos.filter(tipo=tipo_filtro)
    
    # Aplicar búsqueda
    if search:
        documentos = documentos.filter(
            Q(titulo__icontains=search) |
            Q(descripcion__icontains=search) |
            Q(url__icontains=search)
        )
    
    # Aplicar ordenamiento
    valid_sorts = ['titulo', 'fecha_carga', 'clasificacion', 'tipo'] # Agregamos 'tipo'
    if sort_by in valid_sorts:
        if order == 'desc':
            sort_by = f'-{sort_by}'
        documentos = documentos.order_by(sort_by)
    
    # Paginación
    paginator = Paginator(documentos, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    admins = User.objects.filter(tipo='admin')
    
    context = {
        'documentos': page_obj,
        'administradores': admins,
        'sort_by': sort_by.replace('-', ''),
        'order': order,
        'clasificacion_filtro': clasificacion,
        'tipo_filtro': tipo_filtro,          
        'tipos_choices': Documento.TIPO_CHOICES,
        'search': search,
    }
    
    return render(request, 'myapp/lista_documentos.html', context)



@login_required
def subir_documento(request):
    User = get_user_model()

    if request.method == 'POST':
        try:
            titulo = request.POST.get('titulo', '').strip()
            url = request.POST.get('url', '').strip()
            descripcion = request.POST.get('descripcion', '').strip()
            clasificacion = request.POST.get('clasificacion')
            tipo = request.POST.get('tipo', 'reporte') 
            
            # Validaciones
            if not titulo or not url or not clasificacion:
                messages.error(request, 'Título, URL y Clasificación son obligatorios')
                return redirect('panel_documentos')
            
            if not url.startswith(('http://', 'https://')):
                messages.error(request, 'La URL debe comenzar con http:// o https://')
                return redirect('panel_documentos')
            
            # Crear instancia
            documento = Documento(
                titulo=titulo,
                url=url,
                descripcion=descripcion,
                clasificacion=clasificacion,
                tipo=tipo,  # NUEVO: Asignamos el tipo
                clave_admin=request.user
            )
            
            documento.save()
            
            messages.success(request, f'Documento "{titulo}" creado exitosamente')
            
        except Exception as e:
            print(f"Error detallado: {e}")
            messages.error(request, f'Error al crear documento: {str(e)}')
        
        return redirect('panel_documentos')
    
    return redirect('panel_documentos')

@login_required
def editar_documento(request, id):
    documento = get_object_or_404(Documento, id_documento=id)

    if request.method == 'POST':
        try:
            documento.titulo = request.POST.get('titulo', '').strip()
            documento.url = request.POST.get('url', '').strip()
            documento.descripcion = request.POST.get('descripcion', '').strip()
            documento.clasificacion = request.POST.get('clasificacion')
            documento.tipo = request.POST.get('tipo') # NUEVO: Actualizar tipo

            if not documento.url.startswith(('http://', 'https://')):
                return JsonResponse({'success': False, 'error': 'URL inválida'})

            documento.clave_admin = request.user
            documento.save()
            
            return JsonResponse({'success': True, 'message': 'Actualizado correctamente'})

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})


    return render(request, 'myapp/editar_documento.html', {
        'documento': documento,
        'tipos_choices': Documento.TIPO_CHOICES, # NUEVO
        'clasificacion_choices': Documento.CLASIFICACION_CHOICES
    })
    
    
@login_required
def eliminar_documento(request, id):
    """Vista para eliminar documento (AJAX)"""
    if request.method == 'POST':
        try:
            documento = get_object_or_404(Documento, id_documento=id)
            titulo = documento.titulo
            documento.delete()
            
            return JsonResponse({
                'success': True,
                'message': f'Documento "{titulo}" eliminado correctamente'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'})

# ==============================================
# VISTAS PARA PÚBLICO GENERAL (Repositorio público)
# ==============================================
def repositorio_publico(request):
    busqueda = request.GET.get('q', '')
    tipo_filtro = request.GET.get('tipo', '') # NUEVO
    
   
    documentos = Documento.objects.filter(clasificacion='publico')
    

    if tipo_filtro in dict(Documento.TIPO_CHOICES):
        documentos = documentos.filter(tipo=tipo_filtro)

    if busqueda:
        documentos = documentos.filter(
            Q(titulo__icontains=busqueda) | 
            Q(descripcion__icontains=busqueda)
        )
    
    documentos = documentos.order_by('-fecha_carga')
    
    paginator = Paginator(documentos, 15)
    page_number = request.GET.get('page')
    documentos_paginados = paginator.get_page(page_number)
    

    total_publicos = Documento.objects.filter(clasificacion='publico').count()

    qs_publicos = Documento.objects.filter(clasificacion='publico')
    stats_tipos = {
        'videos': qs_publicos.filter(tipo='video').count(),
        'reportes': qs_publicos.filter(tipo='reporte').count(),
        'historicos': qs_publicos.filter(tipo='historico').count(),
    }
    
    context = {
        'documentos': documentos_paginados,
        'busqueda': busqueda,
        'tipo_filtro': tipo_filtro,           
        'tipos_choices': Documento.TIPO_CHOICES, 
        'total_publicos': total_publicos,
        'stats_tipos': stats_tipos,
    }
    
    return render(request, 'myapp/repositorio.html', context)


def descargar_documento(request, id):
    """Vista para descargar un documento"""
    documento = get_object_or_404(Documento, id_documento=id)
    
    # Verificar permisos
    if documento.clasificacion == 'publico':
        # Todos pueden descargar documentos públicos
        pass
    elif documento.clasificacion == 'privado' and not request.user.is_authenticated:
        messages.error(request, 'Debes iniciar sesión para descargar este documento')
        return redirect('login') + f'?next={request.path}'
    elif documento.clasificacion == 'confidencial' and not (request.user.is_admin or request.user.is_superuser):
        messages.error(request, 'No tienes permiso para descargar este documento')
        return redirect('repositorio')
    
    try:
        # Intentar redirigir a la URL del documento
        return redirect(documento.url)
        
    except Exception as e:
        messages.error(request, f'Error al acceder al documento: {str(e)}')
        return redirect('repositorio')

# ==============================================
# VISTAS ADICIONALES SIMPLIFICADAS
# ==============================================

@login_required
def ver_documento_detalle(request, id):
    """Vista para ver detalles completos de un documento"""
    documento = get_object_or_404(Documento, id_documento=id)
    
    # Verificar permisos de acceso usando el método del modelo
    # Si tienes el método puede_acceder_usuario en tu modelo
    if hasattr(documento, 'puede_acceder_usuario'):
        if not documento.puede_acceder_usuario(request.user):
            if request.user.is_authenticated:
                messages.error(request, 'No tienes permiso para acceder a este documento')
                return redirect('repositorio')
            else:
                messages.warning(request, 'Debes iniciar sesión para acceder a este documento')
                return redirect('login') + f'?next={request.path}'
    else:
        # Lógica básica de permisos si no existe el método
        if documento.clasificacion == 'privado' and not request.user.is_authenticated:
            messages.warning(request, 'Debes iniciar sesión para acceder a este documento')
            return redirect('login') + f'?next={request.path}'
        elif documento.clasificacion == 'confidencial' and not (request.user.is_admin or request.user.is_superuser):
            messages.error(request, 'No tienes permiso para acceder a este documento')
            return redirect('repositorio')
    
    context = {
        'documento': documento,
        'puede_editar': request.user.is_admin or request.user.is_superuser,
        'puede_eliminar': request.user.is_admin or request.user.is_superuser,
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
    
    # Solo usuarios staff pueden exportar todos los documentos
    if request.user.is_admin or request.user.is_superuser:
        documentos = Documento.objects.all().order_by('id_documento')
        filename = "todos_documentos.csv"
    else:
        # Usuarios normales solo exportan documentos accesibles
        documentos = Documento.objects.filter(
            Q(clasificacion='publico') | 
            Q(clasificacion='privado')
        ).order_by('id_documento')
        filename = "mis_documentos.csv"
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    writer = csv.writer(response)
    writer.writerow(['ID', 'Título', 'Clasificación', 'URL', 'Fecha Carga', 'Administrador'])
    
    for doc in documentos:
        admin_nombre = doc.clave_admin.get_full_name() if doc.clave_admin else ''
        writer.writerow([
            doc.id_documento,
            doc.titulo,
            doc.get_clasificacion_display() if hasattr(doc, 'get_clasificacion_display') else doc.clasificacion,
            doc.url,
            doc.fecha_carga.strftime('%Y-%m-%d'),
            admin_nombre
        ])
    
    return response




def mapa(request):
    archivo_id = request.GET.get('archivo_id')
    
    
    print("[DEBUG MAPA] Iniciando vista mapa")
    
    # Obtener todas las geometrías (con sus puntos de interés relacionados)
    if archivo_id:
        geometrias = GeometriaEspacial.objects.filter(
            id_archivo_id=archivo_id
        ).prefetch_related(
            'punto_interes_set',
            'punto_interes_set__sitio_turistico',
            'punto_interes_set__sitio_turistico__id_categoria',
            'punto_interes_set__servicio',
            'punto_interes_set__ofrenda'
        )
    else:
        geometrias = GeometriaEspacial.objects.all().prefetch_related(
            'punto_interes_set',
            'punto_interes_set__sitio_turistico',
            'punto_interes_set__sitio_turistico__id_categoria',
            'punto_interes_set__servicio',
            'punto_interes_set__ofrenda'
        )
    
    print(f"[DEBUG MAPA] Total geometrias: {geometrias.count()}")

    features = []

    for geo in geometrias:
        # Obtener el punto de interés relacionado (si existe)
        punto = geo.punto_interes_set.first()
        
        if not punto:
            print(f"[DEBUG MAPA] Geometría {geo.id_geometria} sin punto de interés, saltando...")
            continue
        
        print(f"[DEBUG MAPA] Procesando punto: {punto.nombre} (categoria={punto.categoria})")
        
        # --- DETERMINAR EL NOMBRE DEL FILTRO ---
        nombre_filtro = "Otros" # Fallback
        
        if punto.categoria == 'sitio_turistico':
            if hasattr(punto, 'sitio_turistico') and punto.sitio_turistico and punto.sitio_turistico.id_categoria:
                nombre_filtro = punto.sitio_turistico.id_categoria.nombre
            else:
                nombre_filtro = "Sitios Turísticos"
        
        elif punto.categoria == 'ofrenda':
            nombre_filtro = "Ofrendas"
            
        elif punto.categoria == 'servicio':
            nombre_filtro = "Servicios"

        # Preparamos las propiedades
        propiedades = {
            "nombre": punto.nombre,
            "categoria_filtro": nombre_filtro,
            "categoria_sistema": punto.categoria,
            "categoria_sitio": (
                punto.sitio_turistico.id_categoria.nombre
                if punto.categoria == 'sitio_turistico' and hasattr(punto, 'sitio_turistico') and punto.sitio_turistico and getattr(punto.sitio_turistico, 'id_categoria', None)
                else ""
            ),
            "descripcion": punto.descripcion or "",
            "imagen": str(punto.imagen_portada) if punto.imagen_portada else "",
            "horario": f"{punto.hora_apertura} - {punto.hora_cierre}" if punto.hora_apertura else "Siempre abierto",
            "estado_actual": "Abierto",
            "tipo_geometria": geo.tipo
        }

        # Extra para servicios
        if punto.categoria == 'servicio' and hasattr(punto, 'servicio'):
            propiedades['contacto'] = punto.servicio.contacto or ""

        # Agregar al GeoJSON si tenemos coordenadas en la geometría
        print(f"[DEBUG MAPA] geo.coordenadas = {geo.coordenadas}, type = {type(geo.coordenadas)}")
        print(f"[DEBUG MAPA] geo.propiedades = {geo.propiedades}")
        print(f"[DEBUG MAPA] geo.nombre = {geo.nombre}")
        print(f"[DEBUG MAPA] geo.tipo = {geo.tipo}")
        print(f"[DEBUG MAPA] geo.id_archivo = {geo.id_archivo}")
        if geo.coordenadas:
            features.append({
                "type": "Feature",
                "geometry": geo.coordenadas if isinstance(geo.coordenadas, dict) else json.loads(geo.coordenadas),
                "properties": propiedades
            })
            print(f"[DEBUG MAPA] Agregado punto: {punto.nombre}")
        else:
            print(f"[DEBUG MAPA] Punto {punto.nombre} sin coordenadas o coordenadas vacías")

    print(f"[DEBUG MAPA] Total features generados: {len(features)}")

    geojson_data = {
        "type": "FeatureCollection",
        "features": features
    }

    # --- OBTENER CATEGORÍAS Y SITIOS DE LA BASE DE DATOS ---
    # Obtener todas las categorías de sitios turísticos
    categorias_sitio = Categoria_Sitio.objects.all().order_by('nombre')
    categorias_sitio_data = [
        {'id': cat.id_categoria, 'nombre': cat.nombre}
        for cat in categorias_sitio
    ]
    
    # Obtener todos los sitios turísticos
    sitios_turisticos = Sitio_turistico.objects.all().select_related('id_punto', 'id_categoria')
    sitios_data = [
        {'id': sitio.id_sitio, 'nombre': sitio.id_punto.nombre, 'categoria_id': sitio.id_categoria.id_categoria}
        for sitio in sitios_turisticos
    ]
    
    # Obtener ofrendas
    ofrendas = Ofrenda.objects.all().select_related('id_punto')
    ofrendas_data = [
        {'id': ofrenda.id_ofrenda, 'nombre': ofrenda.id_punto.nombre}
        for ofrenda in ofrendas
    ]
    
    # Obtener servicios
    servicios = Servicio.objects.all().select_related('id_punto')
    servicios_data = [
        {'id': servicio.id_servicio, 'nombre': servicio.id_punto.nombre}
        for servicio in servicios
    ]

    context = {
        'geojson_data': json.dumps(geojson_data, default=str),
        'archivo': None,
        'categorias_sitio': json.dumps(categorias_sitio_data, default=str),
        'sitios_turisticos': json.dumps(sitios_data, default=str),
        'ofrendas': json.dumps(ofrendas_data, default=str),
        'servicios': json.dumps(servicios_data, default=str),
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
                    img_portada = request.POST.get('imagen_portada', '') # <-- Agregado

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
                            # Determinar tipo
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
    return render(request, 'myapp/mod_db/crud_kml.html', {
        'categorias': categorias,
        'archivos': archivos,
    })


@login_required
def detalle_archivo(request, archivo_id):
    try:
        archivo = get_object_or_404(ArchivoKMZ, id_archivo=archivo_id, usuario=request.user)
        # Buscar el punto a través de la geometría
        # Nota: Ajusta 'id_geometria__id_archivo' si tu relación es diferente, 
        # pero basándome en tus modelos parece correcto.
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
                'nombre_punto': punto.nombre,
                'descripcion_punto': punto.descripcion or '',
                'estado_punto': punto.estado,
                'fecha_inicio': format_date(punto.fecha_inicio),
                'fecha_fin': format_date(punto.fecha_fin),
                'hora_apertura': format_time(punto.hora_apertura),
                'hora_cierre': format_time(punto.hora_cierre),
                
                # CORRECCIÓN 1: Imagen Portada (Es URLField, se toma directo)
                'imagen_portada': punto.imagen_portada or '',
                
                # CORRECCIÓN 2: Días de semana (String a Lista)
                'dias_semana': punto.dias_semana.split(',') if punto.dias_semana else [],
            })

            # CORRECCIÓN 3: Galería Multimedia
            # El modelo es Galeria_Multimedia, por defecto Django usa el nombre en minúsculas + _set
            try:
                items_galeria = punto.galeria_multimedia_set.all() 
                galeria_data = []
                for item in items_galeria:
                    galeria_data.append({
                        'id': item.id_foto,          # Según tu modelo: id_foto
                        'url': item.url_archivo,     # Según tu modelo: url_archivo
                        'tipo': item.tipo_archivo    # Según tu modelo: tipo_archivo
                    })
                data['galeria'] = galeria_data
            except Exception as e:
                print(f"Error procesando galería: {e}")
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
                ofrenda = punto.ofrenda
                data.update({
                    'tipo_punto': 'ofrenda',
                    'anfitrion': ofrenda.anfitrion or ''
                })
            elif hasattr(punto, 'servicio'):
                servicio = punto.servicio
                data.update({
                    'tipo_punto': 'servicio',
                    'tipo_servicio': servicio.tipo_servicio,
                    'contacto_servicio': servicio.contacto or '',
                    'tipo_pago': servicio.tipo_pago.split(',') if servicio.tipo_pago else []
                })
            else:
                data['tipo_punto'] = ''

        return JsonResponse(data)

    except Exception as e:
        print(f"ERROR: {str(e)}")
        return JsonResponse({'success': False, 'error': f"Error interno: {str(e)}"}, status=500)
    
    
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

            # Procesamiento de Fechas del Archivo
            fecha_inicio_str = request.POST.get('fecha_inicio')
            if fecha_inicio_str:
                try:
                    fecha_inicio_naive = datetime.datetime.strptime(fecha_inicio_str, '%Y-%m-%dT%H:%M')
                    archivo.fecha_inicio = timezone.make_aware(fecha_inicio_naive)
                except ValueError:
                    pass
            else:
                archivo.fecha_inicio = None

            fecha_fin_str = request.POST.get('fecha_fin')
            if fecha_fin_str:
                try:
                    fecha_fin_naive = datetime.datetime.strptime(fecha_fin_str, '%Y-%m-%dT%H:%M')
                    archivo.fecha_fin = timezone.make_aware(fecha_fin_naive)
                except ValueError:
                    pass
            else:
                archivo.fecha_fin = None

            archivo.save()

            # 2. Actualizar Geometría
            geometria = GeometriaEspacial.objects.filter(id_archivo=archivo).first()
            if geometria:
                geometria.nombre = archivo.nombre_archivo
                geometria.save()

                # 3. Actualizar Punto de Interés
                punto = Punto_Interes.objects.filter(id_geometria=geometria).first()
                
                if punto:
                    punto.nombre = request.POST.get('nombre_punto') or archivo.nombre_archivo
                    punto.descripcion = archivo.descripcion 
                    punto.estado = request.POST.get('estado_punto', punto.estado)
                    
                    punto.fecha_inicio = request.POST.get('fecha_inicio') or punto.fecha_inicio
                    punto.fecha_fin = request.POST.get('fecha_fin') or punto.fecha_fin
                    punto.hora_apertura = request.POST.get('hora_apertura') or punto.hora_apertura
                    punto.hora_cierre = request.POST.get('hora_cierre') or punto.hora_cierre
                    
                    # --- [CORRECCIÓN IMPORTANTE 1: PORTADA Y DÍAS] ---
                    punto.imagen_portada = request.POST.get('imagen_portada', punto.imagen_portada)
                    
                    # Capturamos lista de días (checkboxes)
                    dias_lista = request.POST.getlist('dias_semana')
                    if dias_lista:
                        punto.dias_semana = ",".join(dias_lista)
                    # Nota: Si dias_lista viene vacío, decidimos si borrar o mantener. 
                    # Normalmente en un edit, si no marcas nada, se asume borrar.
                    elif 'dias_semana' in request.POST: # Solo si el campo existía en el form
                         punto.dias_semana = ''
                    
                    punto.save()

                    # 4. Actualizar Subtipos
                    tipo_seleccionado = request.POST.get('tipo_punto', '')

                    if tipo_seleccionado == 'sitio_turistico':
                        id_cat_seleccionada = request.POST.get('id_categoria_bd')
                        if id_cat_seleccionada:
                            categoria_instancia = Categoria_Sitio.objects.get(id_categoria=id_cat_seleccionada)
                            
                            sitio_obj = getattr(punto, 'sitio_turistico', None)
                            reglas = request.POST.get('reglas_acceso', '')
                            
                            if sitio_obj:
                                sitio_obj.id_categoria = categoria_instancia
                                sitio_obj.reglas_acceso = reglas
                                sitio_obj.save()
                            else:
                                Sitio_turistico.objects.create(
                                    id_punto=punto,
                                    id_categoria=categoria_instancia,
                                    reglas_acceso=reglas
                                )

                    elif tipo_seleccionado == 'ofrenda':
                        anfitrion = request.POST.get('anfitrion', 'Sin anfitrión')
                        ofr_obj = getattr(punto, 'ofrenda', None)
                        if ofr_obj:
                            ofr_obj.anfitrion = anfitrion
                            ofr_obj.save()
                        else:
                            Ofrenda.objects.create(id_punto=punto, anfitrion=anfitrion)

                    elif tipo_seleccionado == 'servicio':
                        tipo_servicio_input = request.POST.get('tipo_servicio', 'hospedaje')
                        contacto_input = request.POST.get('contacto_servicio', '')
                        
                        pagos_lista = request.POST.getlist('tipo_pago')
                        if not pagos_lista and request.POST.get('tipo_pago'):
                             pagos_lista = [request.POST.get('tipo_pago')]
                        
                        pagos_str = ",".join(pagos_lista) if pagos_lista else 'efectivo'

                        serv_obj = getattr(punto, 'servicio', None)
                        if serv_obj:
                            serv_obj.tipo_servicio = tipo_servicio_input
                            serv_obj.contacto = contacto_input
                            if pagos_lista:
                                serv_obj.tipo_pago = pagos_str
                            serv_obj.save()
                        else:
                            Servicio.objects.create(
                                id_punto=punto,
                                tipo_servicio=tipo_servicio_input,
                                contacto=contacto_input,
                                tipo_pago=pagos_str
                            )
                    
                    # --- [CORRECCIÓN IMPORTANTE 2: PROCESAR NUEVAS FOTOS DE GALERÍA] ---
                    # Esto faltaba por completo en tu código
                    archivos_galeria = request.FILES.getlist('galeria_multimedia')
                    if archivos_galeria:
                        # Importar almacenamiento local si usas FileSystemStorage
                        from django.core.files.storage import FileSystemStorage
                        fs = FileSystemStorage()
                        
                        for f in archivos_galeria:
                            ext = f.name.split('.')[-1].lower()
                            tipo = 'imagen'
                            if ext in ['mp4', 'avi', 'mov', 'webm']:
                                tipo = 'video'
                            elif ext in ['mp3', 'wav']:
                                tipo = 'audio'
                            
                            # Guardamos archivo físico y obtenemos URL
                            filename = fs.save(f"galeria/{f.name}", f)
                            url_publica = fs.url(filename)

                            Galeria_Multimedia.objects.create(
                                id_punto=punto,
                                url_archivo=url_publica,
                                tipo_archivo=tipo,
                                descripcion=f"Subido el {timezone.now().date()}"
                            )

        return JsonResponse({'success': True, 'message': 'Archivo y datos relacionados actualizados correctamente.'})

    except ArchivoKMZ.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'El archivo no existe o no tienes permiso.'}, status=404)
    except Categoria_Sitio.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'La categoría seleccionada no existe.'}, status=400)
    except Exception as e:
        # Imprimir error en consola para depuración
        print(f"Error en editar_archivo: {str(e)}")
        return JsonResponse({'success': False, 'error': f'Error interno: {str(e)}'}, status=400)




@login_required
def toggle_visibilidad(request, archivo_id):
    """Alterna la visibilidad de un archivo"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Método no permitido'}, status=405)
    
    try:
        archivo = get_object_or_404(ArchivoKMZ, id_archivo=archivo_id, usuario=request.user)
        data = json.loads(request.body)
        archivo.visible = data.get('visible', True)
        archivo.save()
        return JsonResponse({'success': True, 'visible': archivo.visible})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)




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
    categorias = Categoria_Sitio.objects.values('id', 'nombre')
    return JsonResponse(list(categorias), safe=False)

# --- VISTA PARA CREAR CATEGORÍA (MODAL) ---
@login_required
def crear_categoria(request):
    if request.method != 'POST':
        return JsonResponse({'status': 'error'})

    nombre = request.POST.get('nombre', '').strip()
    slug = request.POST.get('codigo_slug', '').strip()

    if not nombre or not slug:
        return JsonResponse({'status': 'error', 'message': 'Datos incompletos'})

    nueva = Categoria_Sitio.objects.create(
        nombre=nombre.title(),
        codigo_slug=slug.lower()
    )

    return JsonResponse({
        'status': 'success',
        'new_id': nueva.id_categoria,
        'new_name': nueva.nombre
    })
    
    
    
    
@login_required
@require_POST # Decorador útil para asegurar que solo sea POST
def procesar_archivo(request, archivo_id):
    # 1. Obtener el objeto
    archivo = get_object_or_404(ArchivoKMZ, id_archivo=archivo_id, usuario=request.user)
    
    # 2. Verificar tipo de archivo (validación rápida antes de instanciar)
    if archivo.tipo_archivo not in ['kml', 'kmz']:
        return JsonResponse({
            'success': False, 
            'error': 'Solo se pueden procesar archivos KML/KMZ'
        }, status=400)

    # 3. Delegar el trabajo al procesador
    processor = KMLProcessor(archivo)
    resultado = processor.procesar()

    # 4. Devolver respuesta basada en el resultado del procesador
    status_code = 200 if resultado['success'] else 500
    return JsonResponse(resultado, status=status_code)


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
def eliminar_archivo(request, archivo_id):
    """Elimina un archivo"""
    if request.method != 'POST':
        messages.error(request, 'Método no permitido')
        return redirect('lista_archivos')
    
    try:
        archivo = get_object_or_404(ArchivoKMZ, id_archivo=archivo_id, usuario=request.user)
        nombre = archivo.nombre_archivo
        archivo.delete()
        messages.success(request, f'Recurso "{nombre}" eliminado exitosamente')
        return redirect('lista_archivos')
    except Exception as e:
        messages.error(request, f'Error al eliminar recurso: {str(e)}')
        return redirect('lista_archivos')

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
            # Redirigir al formulario de registro para encuestadores  
            return redirect('formulario')  
        
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