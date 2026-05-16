"""
API Views para la app móvil del Observatorio de Datos Huaquechula.
Todos los endpoints responden en JSON y usan autenticación JWT.
"""
from django.contrib.auth.models import User
from django.contrib.auth.hashers import check_password

from rest_framework import status, generics, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from rest_framework_simplejwt.tokens import RefreshToken

from .models import (
    Usuario, Encuestador,
    RegistroVisita, PersonaVisita,
    Eje,
    EncuestaResidente, EncuestaComercio,
)
from .serializers import (
    UsuarioSerializer,
    RegistroVisitaSerializer,
    EjeSerializer,
    EncuestaResidenteSerializer,
    EncuestaComercioSerializer,
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

        # Autenticar contra la tabla Usuario personalizada
        try:
            usuario = Usuario.objects.get(nombre_usuario=username)
        except Usuario.DoesNotExist:
            return Response(
                {'error': 'Credenciales incorrectas'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        if not check_password(password, usuario.contrasenia):
            return Response(
                {'error': 'Credenciales incorrectas'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        # Obtener o crear el User de Django (requerido por simplejwt)
        django_user, _ = User.objects.get_or_create(username=usuario.nombre_usuario)

        # Generar tokens JWT
        refresh = RefreshToken.for_user(django_user)
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
            usuario = Usuario.objects.get(nombre_usuario=request.user.username)
            return Response(UsuarioSerializer(usuario).data)
        except Usuario.DoesNotExist:
            return Response({'error': 'Usuario no encontrado'}, status=status.HTTP_404_NOT_FOUND)


# ─── Registros de Visita ───────────────────────────────────────────────────────

def _get_encuestador(request):
    """Helper: retorna el Encuestador asociado al usuario autenticado."""
    usuario = Usuario.objects.get(nombre_usuario=request.user.username)
    if usuario.tipo not in ['encuestador', 'admin']:
        raise PermissionDenied("Solo encuestadores y administradores pueden gestionar visitas.")

    if usuario.tipo == 'encuestador':
        encuestador = Encuestador.objects.get(id_usuario=usuario)
    else:
        encuestador, _ = Encuestador.objects.get_or_create(
            clave_encuestador=f'ADMIN_{usuario.id_usuario}',
            defaults={'id_usuario': usuario}
        )
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

        registros = RegistroVisita.objects.filter(id_encuestador=encuestador).order_by('-fecha')
        serializer = RegistroVisitaSerializer(registros, many=True)
        return Response(serializer.data)

    def post(self, request):
        try:
            encuestador = _get_encuestador(request)
        except (Usuario.DoesNotExist, Encuestador.DoesNotExist):
            return Response({'error': 'Encuestador no encontrado'}, status=status.HTTP_404_NOT_FOUND)

        data = request.data.copy()
        data['id_encuestador'] = encuestador.clave_encuestador

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
    """Helper que retorna el Encuestador o None si no existe en la BD legáda."""
    try:
        usuario = Usuario.objects.get(nombre_usuario=request.user.username)
        if usuario.tipo not in ['encuestador', 'admin']:
            raise PermissionDenied('Solo encuestadores y administradores pueden enviar encuestas.')
        try:
            return Encuestador.objects.get(id_usuario=usuario)
        except Exception:
            return None
    except Usuario.DoesNotExist:
        raise PermissionDenied('Usuario no encontrado.')


class EncuestaResidenteView(APIView):
    """
    GET  /api/mobile/encuestas/residente/  → Lista las encuestas capturadas
    POST /api/mobile/encuestas/residente/  → Crea una nueva encuesta de residente

    Cuerpo POST esperado:
    {
        "edad": 35,
        "genero": "Mujer",
        "barrio_colonia": "Centro",
        "confianza_policia": 3,
        "percepcion_inseguridad": 4,
        "tension_festividades": 2,
        "acceso_servicios_festividades": 3,
        "perdida_tradicion": 2,
        "calidad_aire": 2,
        "gestion_residuos": 2
    }
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
