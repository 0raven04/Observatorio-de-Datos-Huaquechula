"""
Servicio para interactuar con la API del INEGI.
Obtiene indicadores demográficos para el municipio de Huaquechula.
"""
import requests
import logging
from typing import Dict, Optional, List
from datetime import datetime

logger = logging.getLogger(__name__)


class INEGIService:
    """
    Servicio para consultar la API del Banco de Indicadores del INEGI.
    """
    
    # Configuración de la API
    BASE_URL = "https://www.inegi.org.mx/app/api/indicadores/desarrolladores/jsonxml/INDICATOR"
    VERSION = "2.0"
    
    # Código geográfico de Huaquechula, Puebla
    # Puebla = 21, Huaquechula = 071
    HUAQUECHULA_CODE = "21071"
    
    def __init__(self, token: str):
        """
        Inicializa el servicio con el token de autenticación.
        
        Args:
            token: Token de acceso a la API del INEGI
        """
        self.token = token
        if not self.token or self.token == "your_token_here":
            logger.warning("INEGI API token no configurado. Las consultas fallarán.")
    
    def fetch_indicator_data(
        self, 
        indicator_id: str, 
        language: str = "es",
        recent_only: bool = False,
        source: str = "BISE"
    ) -> Optional[Dict]:
        """
        Obtiene datos de un indicador específico del INEGI para Huaquechula.
        
        Args:
            indicator_id: ID del indicador en INEGI (ej. "1002000001" para Población Total)
            language: Idioma de respuesta ('es' o 'en')
            recent_only: Si True, solo obtiene el dato más reciente
            source: Fuente de datos (BISE por defecto)
            
        Returns:
            dict: Datos procesados con estructura {periodo: valor, ...} o None si hay error
        """
        url = self._build_url(indicator_id, language, recent_only, source)
        
        try:
            logger.info(f"Consultando INEGI para indicador {indicator_id}")
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            parsed_data = self._parse_response(data)
            
            logger.info(f"Datos obtenidos exitosamente: {len(parsed_data)} períodos")
            return parsed_data
            
        except requests.exceptions.Timeout:
            logger.error(f"Timeout al consultar INEGI para indicador {indicator_id}")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"Error de red al consultar INEGI: {e}")
            return None
        except Exception as e:
            logger.error(f"Error inesperado al procesar datos de INEGI: {e}")
            return None
    
    def _build_url(
        self, 
        indicator_id: str, 
        language: str, 
        recent_only: bool,
        source: str
    ) -> str:
        """
        Construye la URL de consulta según la especificación INEGI.
        
        Formato: [BASE]/[IdIndicador]/[Idioma]/[AreaGeo]/[DatoReciente]/[Fuente]/[Version]/[Token]?type=json
        """
        recent = 'true' if recent_only else 'false'
        
        url = (
            f"{self.BASE_URL}/"
            f"{indicator_id}/"
            f"{language}/"
            f"{self.HUAQUECHULA_CODE}/"
            f"{recent}/"
            f"{source}/"
            f"{self.VERSION}/"
            f"{self.token}"
            f"?type=json"
        )
        
        return url
    
    def _parse_response(self, json_data: Dict) -> Dict[str, float]:
        """
        Extrae las observaciones de la respuesta JSON del INEGI.
        
        Estructura esperada:
        {
            "Series": [{
                "OBSERVATIONS": [
                    {"TIME_PERIOD": "2020", "OBS_VALUE": "12345"},
                    ...
                ]
            }]
        }
        
        Returns:
            dict: {periodo: valor, ...}
        """
        try:
            # Navegar a Series.OBSERVATIONS
            series = json_data.get('Series', [])
            if not series:
                logger.warning("No se encontraron series en la respuesta")
                return {}
            
            observations = series[0].get('OBSERVATIONS', [])
            if not observations:
                logger.warning("No se encontraron observaciones en la serie")
                return {}
            
            # Extraer TIME_PERIOD y OBS_VALUE
            parsed_data = {}
            for obs in observations:
                period = obs.get('TIME_PERIOD')
                value_str = obs.get('OBS_VALUE')
                
                if period and value_str:
                    try:
                        value = float(value_str)
                        parsed_data[period] = value
                    except ValueError:
                        logger.warning(f"No se pudo convertir valor '{value_str}' a número")
                        continue
            
            return parsed_data
            
        except (KeyError, IndexError, TypeError) as e:
            logger.error(f"Error al parsear respuesta INEGI: {e}")
            return {}
    
    def get_metadata(self, json_data: Dict) -> Dict[str, str]:
        """
        Extrae metadatos de la respuesta (unidad de medida, notas, etc.).
        
        Returns:
            dict: Metadatos del indicador
        """
        try:
            series = json_data.get('Series', [])
            if not series:
                return {}
            
            serie = series[0]
            
            metadata = {
                'unit': serie.get('UNIT', ''),
                'note': serie.get('NOTE', ''),
                'indicator_name': serie.get('INDICADOR', ''),
                'last_update': serie.get('LAST_UPDATE', '')
            }
            
            return metadata
            
        except (KeyError, IndexError, TypeError) as e:
            logger.error(f"Error al extraer metadatos: {e}")
            return {}
    
    def sync_indicator_from_inegi(self, indicador_model, indicator_id: str) -> int:
        """
        Sincroniza un indicador local con datos del INEGI.
        
        Args:
            indicador_model: Instancia del modelo Indicador de Django
            indicator_id: ID del indicador en INEGI
            
        Returns:
            int: Número de mediciones creadas/actualizadas
        """
        from myapp.models import Medicion
        
        # Obtener datos del INEGI
        data = self.fetch_indicator_data(indicator_id)
        
        if not data:
            logger.warning(f"No se obtuvieron datos para indicador {indicator_id}")
            return 0
        
        count = 0
        
        # Crear/actualizar mediciones
        for periodo, valor in data.items():
            _, created = Medicion.objects.update_or_create(
                indicador=indicador_model,
                periodo=periodo,
                defaults={'valor': valor}
            )
            if created:
                count += 1
                
        # Actualizar fecha de sincronización
        from django.utils import timezone
        indicador_model.last_sync = timezone.now()
        indicador_model.save()
        
        logger.info(f"Sincronizados {count} nuevos registros para {indicador_model.nombre}")
        return count
    
    def fetch_jsonstat_data(
        self,
        indicator_id: str,
        language: str = "es",
        recent_only: bool = False,
        source: str = "BISE"
    ) -> Optional[Dict]:
        """
        Obtiene datos en formato JSON-stat del INEGI.
        
        Args:
            indicator_id: ID del indicador en INEGI
            language: Idioma de respuesta
            recent_only: Si True, solo datos recientes
            source: Fuente de datos
            
        Returns:
            dict: Datos en formato JSON-stat o None si hay error
        """
        url = self._build_jsonstat_url(indicator_id, language, recent_only, source)
        
        try:
            logger.info(f"Consultando INEGI JSON-stat para indicador {indicator_id}")
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            # Convertir respuesta INEGI a formato JSON-stat
            jsonstat_data = self._convert_to_jsonstat(data, indicator_id)
            
            logger.info(f"Datos JSON-stat obtenidos exitosamente")
            return jsonstat_data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error al consultar INEGI JSON-stat: {e}")
            return None
        except Exception as e:
            logger.error(f"Error inesperado: {e}")
            return None
    
    def _build_jsonstat_url(
        self,
        indicator_id: str,
        language: str,
        recent_only: bool,
        source: str
    ) -> str:
        """
        Construye URL para consulta JSON-stat.
        Nota: INEGI puede no tener endpoint específico JSON-stat,
        usamos el mismo y convertimos la respuesta.
        """
        return self._build_url(indicator_id, language, recent_only, source)
    
    def _convert_to_jsonstat(self, inegi_data: Dict, indicator_id: str) -> Dict:
        """
        Convierte respuesta INEGI tradicional a formato JSON-stat.
        
        Args:
            inegi_data: Respuesta original del INEGI
            indicator_id: ID del indicador
            
        Returns:
            dict: Datos en formato JSON-stat 2.0
        """
        from myapp.services.jsonstat_utils import build_simple_timeseries
        
        # Extraer datos
        parsed_data = self._parse_response(inegi_data)
        metadata = self.get_metadata(inegi_data)
        
        if not parsed_data:
            return {}
        
        # Construir dataset JSON-stat
        periods = list(parsed_data.keys())
        values = list(parsed_data.values())
        
        jsonstat = build_simple_timeseries(
            indicator_name=metadata.get('indicator_name', f'Indicador {indicator_id}'),
            periods=periods,
            values=values,
            unit=metadata.get('unit', ''),
            source='INEGI'
        )
        
        # Agregar metadatos adicionales
        if metadata.get('note'):
            jsonstat['note'] = [metadata['note']]
        if metadata.get('last_update'):
            jsonstat['updated'] = metadata['last_update']
        
        return jsonstat
    
    def compare_municipalities(
        self,
        indicator_id: str,
        municipality_codes: List[str],
        language: str = "es"
    ) -> Optional[Dict]:
        """
        Compara un indicador entre múltiples municipios.
        Retorna datos en formato JSON-stat multidimensional.
        
        Args:
            indicator_id: ID del indicador en INEGI
            municipality_codes: Lista de códigos municipales (ej: ['21071', '21114'])
            language: Idioma
            
        Returns:
            dict: Dataset JSON-stat con dimensiones [area, time]
        """
        from myapp.services.jsonstat_utils import build_comparative_dataset
        
        # Diccionario para nombres de municipios
        municipality_names = {
            '21071': 'Huaquechula',
            '21114': 'Puebla',
            '21156': 'Atlixco',
            '21119': 'San Martín Texmelucan',
            # Agregar más según necesidad
        }
        
        all_data = []
        all_periods = set()
        
        # Obtener datos para cada municipio
        for code in municipality_codes:
            # Temporalmente cambiar el código de área
            original_code = self.HUAQUECHULA_CODE
            self.HUAQUECHULA_CODE = code
            
            data = self.fetch_indicator_data(indicator_id, language)
            
            # Restaurar código original
            self.HUAQUECHULA_CODE = original_code
            
            if data:
                all_data.append(data)
                all_periods.update(data.keys())
            else:
                all_data.append({})
        
        if not all_data or not all_periods:
            logger.warning("No se pudieron obtener datos para comparación")
            return None
        
        # Ordenar períodos
        sorted_periods = sorted(list(all_periods))
        
        # Construir matriz de valores
        values_matrix = []
        for muni_data in all_data:
            muni_values = [muni_data.get(period, 0.0) for period in sorted_periods]
            values_matrix.append(muni_values)
        
        # Construir nombres de áreas
        areas = {code: municipality_names.get(code, code) for code in municipality_codes}
        
        # Crear dataset JSON-stat comparativo
        jsonstat = build_comparative_dataset(
            indicator_name=f"Indicador {indicator_id}",
            areas=areas,
            periods=sorted_periods,
            values=values_matrix,
            source='INEGI'
        )
        
        return jsonstat


# Mapeo de indicadores locales a IDs de INEGI
# Este mapeo debe actualizarse según los indicadores específicos disponibles
INEGI_INDICATOR_MAPPING = {
    # Salud
    'esperanza_vida': '6207019048',  # Esperanza de vida al nacer
    'mortalidad_infantil': '6207019049',  # Tasa de mortalidad infantil
    
    # Educación
    'escolaridad_promedio': '6207019050',  # Grado promedio de escolaridad
    
    # Población
    'poblacion_total': '1002000001',  # Población total
    
    # Pobreza
    'poblacion_pobreza': '6200240364',  # Población en situación de pobreza
    
    # Agregar más según disponibilidad en INEGI
}


def get_inegi_service() -> Optional[INEGIService]:
    """
    Factory function para obtener una instancia del servicio INEGI.
    Lee el token desde settings de Django.
    
    Returns:
        INEGIService o None si no está configurado
    """
    from django.conf import settings
    
    token = getattr(settings, 'INEGI_API_TOKEN', None)
    
    if not token:
        logger.warning("INEGI_API_TOKEN no configurado en settings")
        return None
    
    return INEGIService(token)
