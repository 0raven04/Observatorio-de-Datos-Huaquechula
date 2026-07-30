"""
API Views para la app móvil del Observatorio de Datos Huaquechula.
Todos los endpoints responden en JSON y usan autenticación JWT.
"""
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password
from django.db import transaction

from rest_framework import status, generics, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from rest_framework_simplejwt.tokens import RefreshToken

from .models import (
    Usuario, Encuestador,
    RegistroVisita,
    Eje,
    EncuestaVisitante, EncuestaResidente, EncuestaInstitucional, EncuestaComercio,
    Encuesta, Pregunta, OpcionPregunta, RespuestaEncuesta, RespuestaPregunta
)
from .serializers import (
    UsuarioSerializer,
    RegistroVisitaSerializer,
    EjeSerializer,
    EncuestaVisitanteSerializer,
    EncuestaResidenteSerializer,
    EncuestaInstitucionalSerializer,
    EncuestaComercioSerializer,
    EncuestaCreadaSerializer,
)


# ─── Autenticación ────────────────────────────────────────────────────────────

class LoginMobileView(APIView):
    """
    POST /api/mobile/login/
    Body: { "username": "...", "password": "..." }
    Respuesta: { "access": "...", "refresh": "...", "usuario": {...} }

    Usa el UsuarioBackend personalizado del proyecto (tabla Usuario, no auth_user).
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        username = request.data.get('username', '').strip()
        password = request.data.get('password', '')

        if not username or not password:
            return Response(
                {'error': 'Se requieren usuario y contraseña'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Autenticar contra la tabla Usuario personalizada (búsqueda insensible a mayúsculas)
        try:
            usuario = Usuario.objects.get(nombre_usuario__iexact=username)
        except Usuario.DoesNotExist:
            return Response(
                {'error': 'Credenciales incorrectas (Usuario no encontrado)'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        if not check_password(password, usuario.password):
            return Response(
                {'error': 'Credenciales incorrectas (Contraseña no válida)'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        # Generar tokens JWT directamente con el Usuario personalizado
        refresh = RefreshToken.for_user(usuario)
        # Embeber el tipo de usuario en el token para uso en la app
        refresh['tipo_usuario'] = usuario.tipo
        refresh['id_usuario'] = usuario.id_usuario

        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'usuario': UsuarioSerializer(usuario).data
        }, status=status.HTTP_200_OK)


class PerfilView(APIView):
    """
    GET /api/mobile/perfil/
    Retorna los datos del usuario autenticado.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        try:
            usuario = Usuario.objects.get(nombre_usuario=request.user.nombre_usuario)
            return Response(UsuarioSerializer(usuario).data)
        except Usuario.DoesNotExist:
            return Response({'error': 'Usuario no encontrado'}, status=status.HTTP_404_NOT_FOUND)


# ─── Registros de Visita ───────────────────────────────────────────────────────

def _get_encuestador(request):
    """Helper: retorna el Encuestador asociado al usuario autenticado."""
    usuario = Usuario.objects.get(nombre_usuario=request.user.nombre_usuario)
    if usuario.tipo not in ['encuestador', 'admin']:
        raise PermissionDenied("Solo encuestadores y administradores pueden gestionar visitas.")

    encuestador, _ = Encuestador.objects.get_or_create(id_usuario=usuario)
    return encuestador


class VisitasListCreateView(APIView):
    """
    GET  /api/mobile/visitas/  → Lista todos los registros del encuestador
    POST /api/mobile/visitas/  → Crea un nuevo registro con sus personas
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        try:
            encuestador = _get_encuestador(request)
        except (Usuario.DoesNotExist, Encuestador.DoesNotExist):
            return Response({'error': 'Encuestador no encontrado'}, status=status.HTTP_404_NOT_FOUND)

        # Filtros opcionales de fecha
        fecha_desde = request.query_params.get('fecha_desde')
        fecha_hasta = request.query_params.get('fecha_hasta')
        registros = RegistroVisita.objects.filter(clave_encuestador=encuestador).order_by('-fecha')
        if fecha_desde:
            registros = registros.filter(fecha__date__gte=fecha_desde)
        if fecha_hasta:
            registros = registros.filter(fecha__date__lte=fecha_hasta)

        # Paginación manual (?page=1&page_size=20)
        try:
            page = max(1, int(request.query_params.get('page', 1)))
            page_size = min(100, max(1, int(request.query_params.get('page_size', 20))))
        except (ValueError, TypeError):
            page = 1
            page_size = 20
        start = (page - 1) * page_size
        end = start + page_size
        total = registros.count()
        registros_paginados = registros[start:end]
        serializer = RegistroVisitaSerializer(registros_paginados, many=True)
        return Response({
            'total': total,
            'pagina': page,
            'pagina_size': page_size,
            'siguiente': page * page_size < total,
            'datos': serializer.data,
        })

    def post(self, request):
        try:
            encuestador = _get_encuestador(request)
        except (Usuario.DoesNotExist, Encuestador.DoesNotExist):
            return Response({'error': 'Encuestador no encontrado'}, status=status.HTTP_404_NOT_FOUND)

        data = request.data.copy()
        data['clave_encuestador'] = encuestador.clave_encuestador

        # Mapear motivos y transportes a los choices válidos del modelo
        motivo_map = {
            'turismo': 'turismo', 'trabajo': 'negocios', 'negocios': 'negocios',
            'estudios': 'estudios', 'visita familiar': 'visita_familiar',
            'visita_familiar': 'visita_familiar', 'evento': 'otros', 'otro': 'otros',
            'otros': 'otros', 'cultura / tradición': 'turismo',
        }
        transporte_map = {
            'automovil': 'automovil', 'automóvil': 'automovil', 'autobus': 'autobus',
            'autobús': 'autobus', 'avion': 'avion', 'avión': 'avion', 'tren': 'tren',
            'otro': 'otros', 'otros': 'otros',
        }

        motivo_raw = str(data.get('motivo_visita', '')).lower().strip()
        data['motivo_visita'] = motivo_map.get(motivo_raw, 'turismo')

        transporte_raw = str(data.get('tipo_transporte', '')).lower().strip()
        data['tipo_transporte'] = transporte_map.get(transporte_raw, 'automovil')

        if 'visitas_previas' not in data and 'numero_visitas' in data:
            data['visitas_previas'] = data['numero_visitas']

        personas_input = data.get('personas_input', [])
        if personas_input:
            for p in personas_input:
                edad = p.get('edad', 0)
                sexo = str(p.get('sexo', '')).lower()
                prefix = 'mujeres' if sexo in ['femenino', 'f', 'mujer', 'mujeres'] else 'hombres'
                if edad <= 15:
                    key = f'{prefix}_0_15'
                elif edad <= 30:
                    key = f'{prefix}_16_30'
                elif edad <= 45:
                    key = f'{prefix}_31_45'
                elif edad <= 60:
                    key = f'{prefix}_46_60'
                elif edad <= 75:
                    key = f'{prefix}_61_75'
                else:
                    key = f'{prefix}_76_mas'
                data[key] = data.get(key, 0) + 1

        serializer = RegistroVisitaSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VisitaDetailView(APIView):
    """
    GET    /api/mobile/visitas/<id>/  → Detalle de un registro
    PUT    /api/mobile/visitas/<id>/  → Actualizar registro
    DELETE /api/mobile/visitas/<id>/  → Eliminar registro
    """
    permission_classes = [permissions.IsAuthenticated]

    def _get_registro(self, pk):
        try:
            return RegistroVisita.objects.get(pk=pk)
        except RegistroVisita.DoesNotExist:
            return None

    def get(self, request, pk):
        registro = self._get_registro(pk)
        if not registro:
            return Response({'error': 'Registro no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        serializer = RegistroVisitaSerializer(registro)
        return Response(serializer.data)

    def put(self, request, pk):
        registro = self._get_registro(pk)
        if not registro:
            return Response({'error': 'Registro no encontrado'}, status=status.HTTP_404_NOT_FOUND)

        serializer = RegistroVisitaSerializer(registro, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        registro = self._get_registro(pk)
        if not registro:
            return Response({'error': 'Registro no encontrado'}, status=status.HTTP_404_NOT_FOUND)

        serializer = RegistroVisitaSerializer(registro, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        registro = self._get_registro(pk)
        if not registro:
            return Response({'error': 'Registro no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        registro.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ─── Indicadores del Observatorio ─────────────────────────────────────────────

class IndicadoresView(APIView):
    """
    GET /api/mobile/indicadores/
    Retorna todos los ejes con sus categorías, indicadores y mediciones.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        ejes = Eje.objects.prefetch_related(
            'categorias__indicadores__mediciones'
        ).all()
        serializer = EjeSerializer(ejes, many=True)
        return Response(serializer.data)


class DashboardSummaryView(APIView):
    """
    GET /api/mobile/dashboard/
    Retorna un resumen compacto: por cada indicador, solo la última medición.
    Útil para la pantalla de inicio de la app sin cargar todos los datos históricos.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        ejes = Eje.objects.prefetch_related('categorias__indicadores__mediciones').all()
        resultado = []

        for eje in ejes:
            eje_data = {'id': eje.id, 'nombre': eje.nombre, 'categorias': []}
            for categoria in eje.categorias.all():
                cat_data = {'id': categoria.id, 'nombre': categoria.nombre, 'indicadores': []}
                for indicador in categoria.indicadores.all():
                    ultima = indicador.mediciones.order_by('-periodo').first()
                    cat_data['indicadores'].append({
                        'id': indicador.id,
                        'nombre': indicador.nombre,
                        'unidad_medida': indicador.unidad_medida,
                        'ultima_medicion': {
                            'periodo': ultima.periodo,
                            'valor': str(ultima.valor)
                        } if ultima else None
                    })
                eje_data['categorias'].append(cat_data)
            resultado.append(eje_data)

        return Response(resultado)


# ─── Encuestas ───────────────────────────────────────────────────────────────

def _get_encuestador_safe(request):
    """Helper que retorna el Encuestador o None si no existe en la BD legada."""
    try:
        usuario = Usuario.objects.get(nombre_usuario=request.user.nombre_usuario)
        if usuario.tipo not in ['encuestador', 'admin']:
            raise PermissionDenied('Solo encuestadores y administradores pueden enviar encuestas.')
        encuestador, _ = Encuestador.objects.get_or_create(id_usuario=usuario)
        return encuestador
    except Usuario.DoesNotExist:
        raise PermissionDenied('Usuario no encontrado.')


class EncuestaVisitanteView(APIView):
    """
    GET  /api/mobile/encuestas/visitante/  → Lista encuestas de visitante
    POST /api/mobile/encuestas/visitante/  → Registra Encuesta: Perfil del Visitante
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        encuestas = EncuestaVisitante.objects.all().order_by('-fecha')
        serializer = EncuestaVisitanteSerializer(encuestas, many=True)
        return Response(serializer.data)

    def post(self, request):
        encuestador = _get_encuestador_safe(request)
        data = request.data.copy()

        # Si zonas_visitadas o actividades vienen como listas, unirlas por comas
        if isinstance(data.get('zonas_visitadas'), list):
            data['zonas_visitadas'] = ', '.join(data['zonas_visitadas'])
        if isinstance(data.get('actividades'), list):
            data['actividades'] = ', '.join(data['actividades'])

        serializer = EncuestaVisitanteSerializer(data=data)
        if serializer.is_valid():
            serializer.save(encuestador=encuestador)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EncuestaResidenteView(APIView):
    """
    GET  /api/mobile/encuestas/residente/  → Lista las encuestas capturadas
    POST /api/mobile/encuestas/residente/  → Crea una nueva encuesta de residente
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        encuestas = EncuestaResidente.objects.all().order_by('-fecha')
        serializer = EncuestaResidenteSerializer(encuestas, many=True)
        return Response(serializer.data)

    def post(self, request):
        encuestador = _get_encuestador_safe(request)
        serializer = EncuestaResidenteSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(encuestador=encuestador)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EncuestaInstitucionalView(APIView):
    """
    GET  /api/mobile/encuestas/institucional/  → Lista encuestas institucionales
    POST /api/mobile/encuestas/institucional/  → Registra Encuesta: Institucional
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        encuestas = EncuestaInstitucional.objects.all().order_by('-fecha')
        serializer = EncuestaInstitucionalSerializer(encuestas, many=True)
        return Response(serializer.data)

    def post(self, request):
        encuestador = _get_encuestador_safe(request)
        data = request.data.copy()

        # Si canales_difusion viene como lista, unirlos por comas
        if isinstance(data.get('canales_difusion'), list):
            data['canales_difusion'] = ', '.join(data['canales_difusion'])

        serializer = EncuestaInstitucionalSerializer(data=data)
        if serializer.is_valid():
            serializer.save(encuestador=encuestador)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MisEncuestasView(APIView):
    """
    GET /api/mobile/mis-encuestas/
    Retorna la lista unificada de todas las encuestas capturadas por el usuario:
    - Encuestas de Visitante
    - Encuestas de Residente
    - Encuestas Institucionales
    - Encuestas de Comercio
    - Respuestas a Encuestas Dinámicas
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        encuestador = _get_encuestador_safe(request)
        usuario = request.user

        resultado = []

        # 1. Visitante
        visitantes = EncuestaVisitante.objects.filter(encuestador=encuestador).order_by('-fecha') if encuestador else EncuestaVisitante.objects.all().order_by('-fecha')
        for v in visitantes:
            resultado.append({
                'id': f"visitante_{v.id}",
                'tipo': "Encuesta: Perfil del Visitante",
                'tipo_codigo': 'visitante',
                'icono': '🗺️',
                'fecha': v.fecha.isoformat(),
                'cargado_bd': True,
                'resumen': f"Origen: {v.residencia_ciudad}, {v.residencia_estado} | Edad: {v.edad}"
            })

        # 2. Residente
        residentes = EncuestaResidente.objects.filter(encuestador=encuestador).order_by('-fecha') if encuestador else EncuestaResidente.objects.all().order_by('-fecha')
        for r in residentes:
            resultado.append({
                'id': f"residente_{r.id}",
                'tipo': "Encuesta: Residente Local",
                'tipo_codigo': 'residente',
                'icono': '🏠',
                'fecha': r.fecha.isoformat(),
                'cargado_bd': True,
                'resumen': f"Barrio: {r.barrio_colonia} | Edad: {r.edad}"
            })

        # 3. Institucional
        institucionales = EncuestaInstitucional.objects.filter(encuestador=encuestador).order_by('-fecha') if encuestador else EncuestaInstitucional.objects.all().order_by('-fecha')
        for i in institucionales:
            resultado.append({
                'id': f"institucional_{i.id}",
                'tipo': "Encuesta: Institucional",
                'tipo_codigo': 'institucional',
                'icono': '🏛️',
                'fecha': i.fecha.isoformat(),
                'cargado_bd': True,
                'resumen': f"Visitantes Festividades: {i.visitantes_festividades:,} | Anual: {i.visitantes_anual:,}"
            })

        # 4. Comercio
        comercios = EncuestaComercio.objects.filter(encuestador=encuestador).order_by('-fecha') if encuestador else EncuestaComercio.objects.all().order_by('-fecha')
        for c in comercios:
            resultado.append({
                'id': f"comercio_{c.id}",
                'tipo': "Encuesta: Comercio",
                'tipo_codigo': 'comercio',
                'icono': '🏪',
                'fecha': c.fecha.isoformat(),
                'cargado_bd': True,
                'resumen': f"Tipo de comercio: {c.tipo_comercio}"
            })

        # 5. Respuestas dinámicas
        try:
            respuestas_din = RespuestaEncuesta.objects.filter(usuario_responde=usuario).order_by('-fecha_envio')
            for rd in respuestas_din:
                resultado.append({
                    'id': f"dinamica_{rd.id}",
                    'tipo': f"Encuesta: {rd.encuesta.titulo}",
                    'tipo_codigo': 'dinamica',
                    'icono': '📋',
                    'fecha': rd.fecha_envio.isoformat(),
                    'cargado_bd': True,
                    'resumen': f"Encuesta personalizada #{rd.encuesta.id}"
                })
        except Exception:
            pass

        # Ordenar por fecha descendente
        resultado.sort(key=lambda x: x['fecha'], reverse=True)
        return Response(resultado)


class EncuestaComercioView(APIView):
    """
    GET  /api/mobile/encuestas/comercio/  → Lista las encuestas capturadas
    POST /api/mobile/encuestas/comercio/  → Crea una nueva encuesta de comercio

    Cuerpo POST esperado:
    {
        "tipo_comercio": "Artesanía",
        "participacion_decisiones": 2,
        "capacitacion_turistica": 1,
        "integracion_turistica": 2
    }
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        encuestas = EncuestaComercio.objects.all().order_by('-fecha')
        serializer = EncuestaComercioSerializer(encuestas, many=True)
        return Response(serializer.data)

    def post(self, request):
        encuestador = _get_encuestador_safe(request)
        serializer = EncuestaComercioSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(encuestador=encuestador)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ─── Encuestas Creadas / Dinámicas para Móvil ─────────────────────────────────

class EncuestaCreadaListView(generics.ListAPIView):
    """
    GET /api/mobile/encuestas-creadas/
    Retorna la lista de encuestas dinámicas creadas que están activas.
    Incluye sus preguntas y opciones respectivas.
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = EncuestaCreadaSerializer
    queryset = Encuesta.objects.filter(activa=True)


class ResponderEncuestaView(APIView):
    """
    POST /api/mobile/encuestas-creadas/<pk>/responder/
    Recibe las respuestas para una encuesta dinámica específica y las guarda.
    """
    permission_classes = [permissions.IsAuthenticated]

    @transaction.atomic
    def post(self, request, pk):
        import json
        survey = generics.get_object_or_404(Encuesta, pk=pk)
        if not survey.activa:
            return Response({'error': 'La encuesta está desactivada.'}, status=status.HTTP_400_BAD_REQUEST)

        respuestas_data = request.data.get('respuestas', [])
        
        # Validar requeridos en base a lo enviado
        preguntas = survey.preguntas.all()
        errors = {}
        respuestas_dict = {r.get('pregunta_id'): r.get('valor') for r in respuestas_data}

        for p in preguntas:
            val = respuestas_dict.get(p.id)
            if p.requerida and (val is None or val == '' or (isinstance(val, list) and len(val) == 0)):
                errors[p.id] = 'Esta pregunta es obligatoria.'

        if errors:
            return Response({'error': 'Errores de validación', 'detalles': errors}, status=status.HTTP_400_BAD_REQUEST)

        # Determinar si la encuesta es anónima
        usuario_resp = request.user if request.user.is_authenticated else None
        if survey.anonima:
            usuario_resp = None

        # Guardar la respuesta principal
        res_encuesta = RespuestaEncuesta.objects.create(
            encuesta=survey,
            usuario_responde=usuario_resp
        )

        # Guardar las respuestas por pregunta
        for p in preguntas:
            val = respuestas_dict.get(p.id)
            if val is not None and val != '':
                if isinstance(val, list):
                    valor_str = json.dumps(val)
                else:
                    valor_str = str(val)

                RespuestaPregunta.objects.create(
                    respuesta_encuesta=res_encuesta,
                    pregunta=p,
                    valor_texto=valor_str
                )

        return Response({'status': 'success', 'respuesta_encuesta_id': res_encuesta.id}, status=status.HTTP_201_CREATED)
