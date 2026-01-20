import math
import zipfile
import io
import urllib.request
import xml.etree.ElementTree as ET
from django.utils import timezone
from .models import GeometriaEspacial
import json  # Asegúrate de importar json
from django.db import transaction

class KMLProcessor:
    def __init__(self, archivo_db):
        """
        Recibe el objeto del modelo ArchivoKMZ (base de datos)
        """
        self.archivo_db = archivo_db
        self.namespace = {'kml': 'http://www.opengis.net/kml/2.2'}

    def procesar(self):
        """Método principal orquestador"""
        try:
            # 1. Descargar y 2. Obtener XML (igual que antes)
            contenido_raw = self._descargar_archivo()
            xml_content = self._obtener_xml_content(contenido_raw)

            # 3. Parsear
            geometrias_extraidas = self._parsear_xml(xml_content)

            # 4. Guardar en BD (CON ATOMICIDAD)
            # Si hay error dentro de este bloque, se deshacen todos los inserts
            with transaction.atomic():
                # Opcional: Borrar geometrías anteriores si re-procesas el mismo archivo
                GeometriaEspacial.objects.filter(id_archivo=self.archivo_db).delete()
                
                contador = self._guardar_en_bd(geometrias_extraidas)

                # 5. Actualizar estatus (dentro de la transacción para asegurar coherencia)
                self.archivo_db.procesado = True
                self.archivo_db.procesado_en = timezone.now()
                self.archivo_db.num_geometrias = contador
                self.archivo_db.error_procesamiento = None
                self.archivo_db.save()

            return {
                'success': True,
                'num_geometrias': contador,
                'message': f'Procesado exitosamente. {contador} geometrías extraídas.'
            }

        except Exception as e:
            # Esto queda fuera del atomic, para poder guardar el error
            self.archivo_db.error_procesamiento = str(e)
            self.archivo_db.save()
            return {'success': False, 'error': str(e)}

    def _descargar_archivo(self):
        """Descarga el archivo desde URL o lo lee localmente"""
        # Verificar si archivo_path es una URL o un archivo local
        if hasattr(self.archivo_db, 'archivo') and self.archivo_db.archivo:
            # Es un FileField de Django
            self.archivo_db.archivo.open('rb')
            return self.archivo_db.archivo.read()
        elif hasattr(self.archivo_db, 'archivo_path'):
            # Es una URL externa
            with urllib.request.urlopen(self.archivo_db.archivo_path, timeout=30) as response:
                return response.read()
        else:
            raise Exception("No se pudo acceder al archivo")

    def _obtener_xml_content(self, contenido_raw):
        """Decide si descomprimir (KMZ) o leer directo (KML)"""
        if self.archivo_db.tipo_archivo == 'kmz':
            # Es un ZIP. Buscamos el archivo .kml dentro (usualmente doc.kml)
            with zipfile.ZipFile(io.BytesIO(contenido_raw)) as z:
                # Buscar el primer archivo que termine en .kml
                kml_files = [f for f in z.namelist() if f.lower().endswith('.kml')]
                if not kml_files:
                    raise Exception("El archivo KMZ no contiene ningún archivo .kml válido")
                # Leemos el primero que encontremos
                return z.read(kml_files[0])
        else:
            # Es KML directo
            return contenido_raw

    def _parsear_xml(self, xml_bytes):
        """Tu lógica original, adaptada para recibir bytes"""
        try:
            # Usamos BytesIO para convertir bytes en un "archivo virtual" que ET puede leer
            tree = ET.parse(io.BytesIO(xml_bytes))
            root = tree.getroot()
            geometrias = []
            
            # Encontrar el elemento Document (si existe) o buscar directamente Placemarks
            document = root.find('.//kml:Document', self.namespace)
            search_root = document if document is not None else root
            
            for placemark in search_root.findall('.//kml:Placemark', self.namespace):
                geometria_data = self._procesar_placemark(placemark)
                if geometria_data:
                    geometrias.append(geometria_data)
            
            return geometrias
        except ET.ParseError as e:
            raise Exception(f"Error parseando XML: {str(e)}")

    def _guardar_en_bd(self, lista_geometrias):
        """Itera sobre los diccionarios y crea los objetos Django"""
        creados = 0
        for geo in lista_geometrias:
            # Crear estructura GeoJSON completa
            geojson_feature = {
                'type': 'Feature',
                'geometry': {
                    'type': geo['tipo'],
                    'coordinates': geo['coordenadas']
                },
                'properties': {
                    'nombre': geo['nombre'],
                    'descripcion': geo.get('descripcion', ''),
                    **geo.get('propiedades', {})
                }
            }
            
            # Crear el objeto GeometriaEspacial
            GeometriaEspacial.objects.create(
                id_archivo=self.archivo_db,
                nombre=geo['nombre'][:255],  # Limitar a 255 caracteres
                tipo=self._mapear_tipo(geo['tipo']),  # Mapear a tu formato
                coordenadas=geo['coordenadas'],  # Solo las coordenadas
                propiedades=geo.get('propiedades', {}),  # Propiedades adicionales
                # Opcional: calcular área y perímetro si es polígono
                area=self._calcular_area(geo) if geo['tipo'] == 'Polygon' else None,
                perimetro=self._calcular_perimetro(geo) if geo['tipo'] in ['Polygon', 'LineString'] else None
            )
            creados += 1
        return creados

    def _mapear_tipo(self, tipo_geojson):
        """Mapea tipos GeoJSON a tus tipos de geometría del modelo"""
        tipo_map = {
            'Point': 'punto',
            'LineString': 'linea',
            'Polygon': 'poligono',
            'MultiPoint': 'multipunto',
            'MultiLineString': 'linea',
            'MultiPolygon': 'multipoligono'
        }
        return tipo_map.get(tipo_geojson, 'desconocido')

    def _calcular_area(self, geometria):
        """Calcula área aproximada para polígonos (en metros cuadrados)"""
        if geometria['tipo'] != 'Polygon' or not geometria['coordenadas']:
            return None
        
        try:
            coords = geometria['coordenadas'][0]  # Anillo exterior
            if len(coords) < 3:
                return None
            
            puntos_calculo = list(coords)
            if puntos_calculo[0] != puntos_calculo[-1]:
                puntos_calculo.append(puntos_calculo[0])
            # Fórmula del área de Gauss
            area = 0
            n = len(coords)
            for i in range(n):
                lon1, lat1 = coords[i]
                lon2, lat2 = coords[(i + 1) % n]
                area += math.radians(lon1) * math.radians(lat2) - math.radians(lon2) * math.radians(lat1)
            
            area = abs(area * 6378137**2 / 2)  # 6378137 = radio de la Tierra en metros
            return round(area, 6)
        except:
            return None

    def _calcular_perimetro(self, geometria):
        """Calcula perímetro aproximado (en metros)"""
        try:
            if geometria['tipo'] == 'Polygon' and geometria['coordenadas']:
                coords = geometria['coordenadas'][0]  # Anillo exterior
            elif geometria['tipo'] == 'LineString':
                coords = geometria['coordenadas']
            else:
                return None
            
            if len(coords) < 2:
                return None
            
            # Importar math para cálculos
            import math
            
            perimetro = 0
            R = 6371000  # Radio de la Tierra en metros
            
            for i in range(len(coords)):
                lon1, lat1 = coords[i]
                lon2, lat2 = coords[(i + 1) % len(coords)]
                
                # Fórmula de haversine
                phi1 = math.radians(lat1)
                phi2 = math.radians(lat2)
                delta_phi = math.radians(lat2 - lat1)
                delta_lambda = math.radians(lon2 - lon1)
                
                a = math.sin(delta_phi/2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda/2)**2
                c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
                perimetro += R * c
            
            return round(perimetro, 6)
        except:
            return None

    # ---------------------------------------------------------
    # TUS MÉTODOS ORIGINALES (con pequeñas mejoras)
    # ---------------------------------------------------------

    def _procesar_placemark(self, placemark):
        try:
            # Extraer nombre
            nombre_elem = placemark.find('kml:name', self.namespace)
            nombre = nombre_elem.text if nombre_elem is not None else "Sin nombre"
            
            # Extraer descripción
            desc_elem = placemark.find('kml:description', self.namespace)
            descripcion = desc_elem.text if desc_elem is not None else ""
            
            # Extraer propiedades extendidas
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
        propiedades = {}
        extended_data = placemark.find('kml:ExtendedData', self.namespace)
        
        if extended_data is not None:
            # Buscar SchemaData
            schema_data = extended_data.find('kml:SchemaData', self.namespace)
            if schema_data is not None:
                for simple_data in schema_data.findall('kml:SimpleData', self.namespace):
                    nombre = simple_data.get('name')
                    valor = simple_data.text
                    if nombre:
                        propiedades[nombre] = valor
            
            # Buscar Data/Value
            for data in extended_data.findall('kml:Data', self.namespace):
                nombre = data.get('name')
                val_elem = data.find('kml:value', self.namespace)
                if nombre and val_elem is not None:
                    propiedades[nombre] = val_elem.text

        return propiedades

    def _extraer_geometria(self, placemark):
        # Buscar MultiGeometry primero
        multi = placemark.find('.//kml:MultiGeometry', self.namespace)
        if multi is not None:
            return self._extraer_multigeometria(multi)
        
        # Geometrías simples
        punto = placemark.find('.//kml:Point', self.namespace)
        if punto is not None: 
            return self._extraer_punto(punto)
        
        linea = placemark.find('.//kml:LineString', self.namespace)
        if linea is not None: 
            return self._extraer_linea(linea)
        
        poligono = placemark.find('.//kml:Polygon', self.namespace)
        if poligono is not None: 
            return self._extraer_poligono(poligono)
        
        return None

    def _extraer_multigeometria(self, multi_elem):
        """Extrae MultiGeometry - devuelve solo la primera geometría por ahora"""
        # Por simplicidad, tomamos la primera geometría encontrada
        punto = multi_elem.find('.//kml:Point', self.namespace)
        if punto is not None: 
            return self._extraer_punto(punto)
        
        linea = multi_elem.find('.//kml:LineString', self.namespace)
        if linea is not None: 
            return self._extraer_linea(linea)
        
        poligono = multi_elem.find('.//kml:Polygon', self.namespace)
        if poligono is not None: 
            return self._extraer_poligono(poligono)
        
        return None

    def _extraer_punto(self, punto_elem):
        coords_elem = punto_elem.find('.//kml:coordinates', self.namespace)
        if coords_elem is None or not coords_elem.text: 
            return None
        
        coords_text = coords_elem.text.strip().replace('\n', '').replace('\t', '')
        coords = [c.strip() for c in coords_text.split(',')]
        
        if len(coords) >= 2:
            try:
                lon = float(coords[0])
                lat = float(coords[1])
                return {'tipo': 'Point', 'coordenadas': [lon, lat]}
            except ValueError:
                return None
        return None

    def _extraer_linea(self, linea_elem):
        coords_elem = linea_elem.find('.//kml:coordinates', self.namespace)
        if coords_elem is None or not coords_elem.text: 
            return None
        
        coordenadas = []
        for coord_line in coords_elem.text.strip().split():
            coords = coord_line.split(',')
            if len(coords) >= 2:
                try:
                    lon = float(coords[0])
                    lat = float(coords[1])
                    coordenadas.append([lon, lat])
                except ValueError:
                    continue
        
        if len(coordenadas) >= 2:
            return {'tipo': 'LineString', 'coordenadas': coordenadas}
        return None

    def _extraer_poligono(self, poligono_elem):
        anillo = poligono_elem.find('.//kml:outerBoundaryIs/kml:LinearRing', self.namespace)
        if anillo is None: 
            return None
        
        coords_elem = anillo.find('.//kml:coordinates', self.namespace)
        if coords_elem is None or not coords_elem.text: 
            return None
        
        coordenadas = []
        for coord_line in coords_elem.text.strip().split():
            coords = coord_line.split(',')
            if len(coords) >= 2:
                try:
                    lon = float(coords[0])
                    lat = float(coords[1])
                    coordenadas.append([lon, lat])
                except ValueError:
                    continue
        
        if len(coordenadas) >= 3:  # Polígono necesita al menos 3 puntos
            return {'tipo': 'Polygon', 'coordenadas': [coordenadas]}
        return None