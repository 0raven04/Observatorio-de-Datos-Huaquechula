import xml.etree.ElementTree as ET
from django.contrib.gis.geos import Point
from .models import GeometriaEspacial
import json

class KMLProcessor:
    def __init__(self, archivo_kml):
        self.archivo_kml = archivo_kml
        self.namespace = {'kml': 'http://www.opengis.net/kml/2.2'}
    
    def procesar_kml(self):
        """Procesa el archivo KML y retorna lista de geometrías procesadas"""
        try:
            tree = ET.parse(self.archivo_kml)
            root = tree.getroot()
            geometrias = []
            
            # Buscar todos los Placemarks
            for placemark in root.findall('.//kml:Placemark', self.namespace):
                geometria_data = self._procesar_placemark(placemark)
                if geometria_data:
                    geometrias.append(geometria_data)
            
            return geometrias
            
        except Exception as e:
            raise Exception(f"Error procesando KML: {str(e)}")
    
    def _procesar_placemark(self, placemark):
        """Procesa un elemento Placemark individual"""
        try:
            # Extraer nombre
            nombre_elem = placemark.find('kml:name', self.namespace)
            nombre = nombre_elem.text if nombre_elem is not None else "Sin nombre"
            
            # Extraer descripción
            desc_elem = placemark.find('kml:description', self.namespace)
            descripcion = desc_elem.text if desc_elem is not None else ""
            
            # Extraer datos extendidos (SchemaData)
            propiedades = self._extraer_propiedades_extendidas(placemark)
            
            # Extraer geometría
            geometria_data = self._extraer_geometria(placemark)
            if not geometria_data:
                return None
            
            return {
                'nombre': nombre,
                'descripcion': descripcion,
                'tipo': geometria_data['tipo'],
                'coordenadas': geometria_data['coordenadas'],
                'propiedades': propiedades
            }
            
        except Exception as e:
            print(f"Error procesando placemark: {e}")
            return None
    
    def _extraer_propiedades_extendidas(self, placemark):
        """Extrae propiedades del ExtendedData/SchemaData"""
        propiedades = {}
        
        extended_data = placemark.find('kml:ExtendedData', self.namespace)
        if extended_data is not None:
            schema_data = extended_data.find('kml:SchemaData', self.namespace)
            if schema_data is not None:
                for simple_data in schema_data.findall('kml:SimpleData', self.namespace):
                    nombre = simple_data.get('name')
                    valor = simple_data.text
                    if nombre and valor:
                        propiedades[nombre] = valor
        
        return propiedades
    
    def _extraer_geometria(self, placemark):
        """Extrae la geometría del Placemark"""
        # Buscar Point
        punto = placemark.find('.//kml:Point', self.namespace)
        if punto is not None:
            return self._extraer_punto(punto)
        
        # Buscar LineString
        linea = placemark.find('.//kml:LineString', self.namespace)
        if linea is not None:
            return self._extraer_linea(linea)
        
        # Buscar Polygon
        poligono = placemark.find('.//kml:Polygon', self.namespace)
        if poligono is not None:
            return self._extraer_poligono(poligono)
        
        return None
    
    def _extraer_punto(self, punto_elem):
        """Extrae coordenadas de punto"""
        coords_elem = punto_elem.find('.//kml:coordinates', self.namespace)
        if coords_elem is None or not coords_elem.text:
            return None
        
        coords_text = coords_elem.text.strip()
        coords = coords_text.split(',')
        
        if len(coords) >= 2:
            # KML usa: longitud,latitud[,altitud]
            # GeoJSON usa: [longitud, latitud]
            return {
                'tipo': 'Point',
                'coordenadas': [float(coords[0]), float(coords[1])]
            }
        return None
    
    def _extraer_linea(self, linea_elem):
        """Extrae coordenadas de línea"""
        coords_elem = linea_elem.find('.//kml:coordinates', self.namespace)
        if coords_elem is None or not coords_elem.text:
            return None
        
        coordenadas = []
        for coord_line in coords_elem.text.strip().split():
            coords = coord_line.split(',')
            if len(coords) >= 2:
                coordenadas.append([float(coords[0]), float(coords[1])])
        
        return {
            'tipo': 'LineString',
            'coordenadas': coordenadas
        }
    
    def _extraer_poligono(self, poligono_elem):
        """Extrae coordenadas de polígono"""
        anillo_exterior = poligono_elem.find('.//kml:outerBoundaryIs/kml:LinearRing', self.namespace)
        if anillo_exterior is None:
            return None
        
        coords_elem = anillo_exterior.find('.//kml:coordinates', self.namespace)
        if coords_elem is None or not coords_elem.text:
            return None
        
        coordenadas = []
        for coord_line in coords_elem.text.strip().split():
            coords = coord_line.split(',')
            if len(coords) >= 2:
                coordenadas.append([float(coords[0]), float(coords[1])])
        
        # En GeoJSON, un polígono es una lista de anillos
        return {
            'tipo': 'Polygon',
            'coordenadas': [coordenadas]
        }