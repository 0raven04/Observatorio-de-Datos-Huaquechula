"""
Utilidades para trabajar con el formato JSON-stat.
Proporciona funciones para construir, parsear y manipular datasets JSON-stat.
"""
from typing import Dict, List, Any, Optional
from datetime import datetime


class JSONStatBuilder:
    """
    Constructor de datasets en formato JSON-stat 2.0.
    Especificación: https://json-stat.org/format/
    """
    
    def __init__(self, label: str, source: str = "INEGI"):
        """
        Inicializa un nuevo dataset JSON-stat.
        
        Args:
            label: Etiqueta descriptiva del dataset
            source: Fuente de los datos
        """
        self.dataset = {
            "version": "2.0",
            "class": "dataset",
            "label": label,
            "source": source,
            "updated": datetime.now().isoformat(),
            "dimension": {
                "id": [],
                "size": []
            },
            "value": []
        }
        self.dimensions = {}
    
    def add_dimension(
        self, 
        dimension_id: str, 
        label: str, 
        categories: Dict[str, str]
    ) -> 'JSONStatBuilder':
        """
        Agrega una dimensión al dataset.
        
        Args:
            dimension_id: ID de la dimensión (ej: 'time', 'area')
            label: Etiqueta descriptiva
            categories: Dict con {id: label} de categorías
            
        Returns:
            Self para encadenamiento
        """
        self.dataset["dimension"]["id"].append(dimension_id)
        self.dataset["dimension"]["size"].append(len(categories))
        
        self.dataset["dimension"][dimension_id] = {
            "label": label,
            "category": {
                "index": list(categories.keys()),
                "label": categories
            }
        }
        
        self.dimensions[dimension_id] = list(categories.keys())
        
        return self
    
    def set_values(self, values: List[float]) -> 'JSONStatBuilder':
        """
        Establece los valores del dataset.
        
        Args:
            values: Lista de valores en orden dimensional
            
        Returns:
            Self para encadenamiento
        """
        self.dataset["value"] = values
        return self
    
    def add_metadata(self, **kwargs) -> 'JSONStatBuilder':
        """
        Agrega metadatos adicionales.
        
        Args:
            **kwargs: Pares clave-valor de metadatos
            
        Returns:
            Self para encadenamiento
        """
        for key, value in kwargs.items():
            self.dataset[key] = value
        return self
    
    def build(self) -> Dict[str, Any]:
        """
        Construye y retorna el dataset JSON-stat completo.
        
        Returns:
            Dict con estructura JSON-stat
        """
        return self.dataset


def build_simple_timeseries(
    indicator_name: str,
    periods: List[str],
    values: List[float],
    unit: str = "",
    source: str = "INEGI"
) -> Dict[str, Any]:
    """
    Construye un dataset JSON-stat simple de serie temporal.
    
    Args:
        indicator_name: Nombre del indicador
        periods: Lista de períodos (años, meses, etc.)
        values: Lista de valores correspondientes
        unit: Unidad de medida
        source: Fuente de datos
        
    Returns:
        Dataset JSON-stat
    """
    builder = JSONStatBuilder(indicator_name, source)
    
    # Agregar dimensión de tiempo
    time_categories = {period: period for period in periods}
    builder.add_dimension("time", "Período", time_categories)
    
    # Establecer valores
    builder.set_values(values)
    
    # Agregar metadatos
    if unit:
        builder.add_metadata(unit={"label": unit})
    
    return builder.build()


def build_comparative_dataset(
    indicator_name: str,
    areas: Dict[str, str],  # {code: name}
    periods: List[str],
    values: List[List[float]],  # values[area_idx][period_idx]
    unit: str = "",
    source: str = "INEGI"
) -> Dict[str, Any]:
    """
    Construye un dataset JSON-stat para comparación entre áreas.
    
    Args:
        indicator_name: Nombre del indicador
        areas: Dict con {código: nombre} de áreas
        periods: Lista de períodos
        values: Matriz de valores [área][período]
        unit: Unidad de medida
        source: Fuente de datos
        
    Returns:
        Dataset JSON-stat multidimensional
    """
    builder = JSONStatBuilder(indicator_name, source)
    
    # Agregar dimensión de área
    builder.add_dimension("area", "Municipio", areas)
    
    # Agregar dimensión de tiempo
    time_categories = {period: period for period in periods}
    builder.add_dimension("time", "Período", time_categories)
    
    # Aplanar valores (JSON-stat usa array unidimensional)
    flat_values = []
    for area_values in values:
        flat_values.extend(area_values)
    
    builder.set_values(flat_values)
    
    # Agregar metadatos
    if unit:
        builder.add_metadata(unit={"label": unit})
    
    return builder.build()


def parse_jsonstat_to_dict(jsonstat_data: Dict[str, Any]) -> Dict[str, List]:
    """
    Parsea un dataset JSON-stat a un formato simple de diccionario.
    
    Args:
        jsonstat_data: Dataset en formato JSON-stat
        
    Returns:
        Dict con {dimension_id: [valores]}
    """
    result = {}
    
    # Extraer dimensiones
    dimension_ids = jsonstat_data.get("dimension", {}).get("id", [])
    
    for dim_id in dimension_ids:
        dim_data = jsonstat_data["dimension"].get(dim_id, {})
        categories = dim_data.get("category", {}).get("index", [])
        result[dim_id] = categories
    
    # Agregar valores
    result["values"] = jsonstat_data.get("value", [])
    
    return result


def extract_time_series(
    jsonstat_data: Dict[str, Any],
    area_code: Optional[str] = None
) -> Dict[str, float]:
    """
    Extrae una serie temporal de un dataset JSON-stat.
    
    Args:
        jsonstat_data: Dataset JSON-stat
        area_code: Código de área (si el dataset es multidimensional)
        
    Returns:
        Dict con {período: valor}
    """
    dimensions = jsonstat_data.get("dimension", {})
    dim_ids = dimensions.get("id", [])
    values = jsonstat_data.get("value", [])
    
    # Obtener categorías de tiempo
    time_dim = dimensions.get("time", {})
    time_periods = time_dim.get("category", {}).get("index", [])
    
    # Si solo hay dimensión de tiempo
    if len(dim_ids) == 1 and dim_ids[0] == "time":
        return {period: values[i] for i, period in enumerate(time_periods)}
    
    # Si hay múltiples dimensiones (área + tiempo)
    if "area" in dim_ids and area_code:
        area_dim = dimensions.get("area", {})
        area_codes = area_dim.get("category", {}).get("index", [])
        
        if area_code not in area_codes:
            return {}
        
        area_idx = area_codes.index(area_code)
        num_periods = len(time_periods)
        
        # Extraer valores para el área específica
        start_idx = area_idx * num_periods
        end_idx = start_idx + num_periods
        area_values = values[start_idx:end_idx]
        
        return {period: area_values[i] for i, period in enumerate(time_periods)}
    
    return {}


def get_metadata(jsonstat_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extrae metadatos de un dataset JSON-stat.
    
    Args:
        jsonstat_data: Dataset JSON-stat
        
    Returns:
        Dict con metadatos
    """
    return {
        "label": jsonstat_data.get("label", ""),
        "source": jsonstat_data.get("source", ""),
        "updated": jsonstat_data.get("updated", ""),
        "unit": jsonstat_data.get("unit", {}).get("label", ""),
        "note": jsonstat_data.get("note", [])
    }
