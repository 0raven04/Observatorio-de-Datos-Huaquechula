"""
Permisos y Throttle personalizados para la API Pública Open Data
del Observatorio de Datos Huaquechula.

Uso:
    class MiVista(APIView):
        permission_classes = [IsPublicAPIKeyValid]
        throttle_classes = [PublicAPIThrottle]
"""
from django.utils import timezone
from rest_framework.permissions import BasePermission
from rest_framework.throttling import SimpleRateThrottle


class IsPublicAPIKeyValid(BasePermission):
    """
    Valida el parámetro ?key=xxx contra el modelo APIKey.
    Si no se proporciona key, se permite el acceso (modo lectura libre).
    Si se proporciona key, debe ser válida y activa.
    """
    message = 'API Key inválida, inactiva o límite diario excedido.'

    def has_permission(self, request, view):
        from .models import APIKey

        api_key = request.query_params.get('key') or request.headers.get('X-API-Key')

        # Sin key: acceso libre (lectura pública)
        if not api_key:
            return True

        try:
            key_obj = APIKey.objects.get(key=api_key, activa=True)
        except APIKey.DoesNotExist:
            return False

        # Verificar límite diario
        if key_obj.ha_excedido_limite:
            self.message = f'Límite diario de {key_obj.limite_diario} solicitudes excedido.'
            return False

        # Incrementar contador de uso
        key_obj.usos_hoy += 1
        key_obj.ultimo_uso = timezone.now()
        key_obj.save(update_fields=['usos_hoy', 'ultimo_uso'])

        # Adjuntar al request para uso en vistas
        request.api_key = key_obj
        return True


class PublicAPIThrottle(SimpleRateThrottle):
    """
    Throttle para endpoints públicos: 500 solicitudes por hora.
    Scope debe coincidir con DEFAULT_THROTTLE_RATES['public_api'] en settings.py.
    """
    scope = 'public_api'

    def get_cache_key(self, request, view):
        # Usar IP del cliente como identificador
        return self.cache_format % {
            'scope': self.scope,
            'ident': self.get_ident(request),
        }
