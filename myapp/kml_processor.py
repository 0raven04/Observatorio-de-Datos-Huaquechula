import math
import zipfile
import io
import xml.etree.ElementTree as ET
from django.utils import timezone
import requests
from .models import GeometriaEspacial
from django.db import transaction
import re
from .models import GeometriaEspacial, Punto_Interes, Ofrenda, Servicio, Sitio_turistico, Categoria_Sitio


class KMLProcessor:
    def __init__(self, archivo_db):
        """
        Recibe el objeto del modelo ArchivoKMZ (base de datos)
        """
        self.archivo_db = archivo_db
        # Cambiamos a la URL correcta del namespace KML
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
                # GeometriaEspacial.objects.filter(id_archivo=self.archivo_db).delete()
                
                contador = self._guardar_en_bd(geometrias_extraidas)

                # 5. Actualizar estatus (dentro de la transacción para asegurar coherencia)
                self.archivo_db.procesado = True
                self.archivo_db.procesado_en = timezone.now()
                # Actualiza el número de geometrías procesadas
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
        url = self.archivo_db.archivo_path
        # ... Tu lógica de descarga existente ...
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            if 'drive.google.com' in url:
                match = re.search(r'/d/([a-zA-Z0-9_-]+)', url)
                if match:
                    file_id = match.group(1)
                    url = f'https://drive.google.com/uc?id={file_id}&export=download'
                else:
                    raise Exception("URL de Google Drive no válida o ID no encontrado.")

            # allow_redirects=True es VITAL para URLs que no son directas
            response = requests.get(url, headers=headers, timeout=30, allow_redirects=True)
            
            # Lanza error si el servidor responde 404, 403, 500, etc.
            response.raise_for_status() 
            
            contenido = response.content

            # 3. VALIDACIÓN DE CONTENIDO (Filtro de seguridad)
            inicio = contenido.strip()[:100].lower()
            if not (inicio.startswith(b'pk') or b'<kml' in inicio or b'<?xml' in inicio):
                if b'<!doctype html' in inicio or b'<html' in inicio:
                    raise Exception("La URL no devolvió un archivo, sino una página web. Revisa los permisos.")
                raise Exception("El archivo descargado no es un KML o KMZ válido.")

            return contenido

        except requests.exceptions.RequestException as e:
            raise Exception(f"Fallo en la conexión: {str(e)}")


    def _obtener_xml_content(self, contenido_raw):
        # ... Tu lógica de obtención de XML existente ...
        if contenido_raw.startswith(b'PK'):
            try:
                with zipfile.ZipFile(io.BytesIO(contenido_raw)) as z:
                    kml_files = [f for f in z.namelist() if f.lower().endswith('.kml')]
                    if not kml_files:
                        raise Exception("El KMZ no contiene archivos .kml")
                    return z.read(kml_files[0])
            except zipfile.BadZipFile:
                return contenido_raw
        else:
            return contenido_raw


# KMLProcessor.py (Reemplaza estos métodos para compatibilidad)

    def _parsear_xml(self, xml_bytes):
        """
        Parsea el XML KML y extrae una lista plana de geometrías.
        """
        try:
            xml_bytes = xml_bytes.strip()
            if not xml_bytes.startswith(b'<'):
                raise Exception(f"Contenido no válido. Empieza con: {xml_bytes[:20]}")

            tree = ET.parse(io.BytesIO(xml_bytes))
            root = tree.getroot()
            ns = {'kml': 'http://www.opengis.net/kml/2.2'}
            
            geometrias_totales = []
            
            # Buscamos todos los Marcadores (Placemarks)
            for placemark in root.findall('.//kml:Placemark', ns):
                # _procesar_placemark ahora devuelve una lista de geometrías planas
                geometrias_placemark = self._procesar_placemark(placemark)
                if geometrias_placemark:
                    geometrias_totales.extend(geometrias_placemark)
            
            return geometrias_totales
        except Exception as e:
            raise Exception(f"Error en el formato XML/KML: {str(e)}")

    def _procesar_placemark(self, placemark):
        """
        Extrae las propiedades y geometrías de un Placemark.
        Retorna una lista plana de diccionarios de geometría (nombre, tipo, coords, props).
        """
        try:
            propiedades = self._extraer_propiedades_extendidas(placemark)
            
            # Intentamos buscar el nombre clásico
            nombre_elem = placemark.find('kml:name', self.namespace)
            if nombre_elem is not None and nombre_elem.text:
                nombre = nombre_elem.text
            else:
                # Rescatamos el nombre de las propiedades (CVEGEO, TIPOMZA, etc.)
                nombre = propiedades.get('Nombre') or propiedades.get('nombre') or "Sin nombre"
            
            desc_elem = placemark.find('kml:description', self.namespace)
            descripcion = desc_elem.text if desc_elem is not None else ""
            
            # _extraer_geometria ahora devuelve una lista de geometrías GeoJSON
            formas_geojson = self._extraer_geometria(placemark)
            if not formas_geojson:
                return None
            
            geometrias_planas = []
            for forma in formas_geojson:
                # Creamos una estructura plana para cada geometría individual
                geometrias_planas.append({
                    'nombre': nombre,
                    'descripcion': descripcion,
                    'tipo': forma['tipo'], # GeoJSON type: Point, LineString, Polygon
                    'coordenadas': forma['coordenadas'],
                    'propiedades': propiedades
                })
            
            return geometrias_planas
        except Exception as e:
            print(f"Error procesando placemark: {e}")
            return None

    def _guardar_en_bd(self, lista_geometrias):
        """Itera sobre los diccionarios y actualiza o crea los objetos Django"""
        creados = 0
        actualizados = 0

        geometrias_existentes = list(GeometriaEspacial.objects.filter(id_archivo=self.archivo_db))
        

        # 1. Contamos cuántas veces aparece cada coordenada en el archivo
        conteo_coords = {}
        for geo in lista_geometrias:
            coord_str = str(geo.get('coordenadas', ''))
            if coord_str and coord_str != '{}':
                conteo_coords[coord_str] = conteo_coords.get(coord_str, 0) + 1

        # 2. Filtramos la lista
        coordenadas_ignoradas = set()
        geometrias_filtradas = []

        for geo in lista_geometrias:
            coord_str = str(geo.get('coordenadas', ''))
            if not coord_str or coord_str == '{}':
                continue

            # Si la coordenada está repetida y NO la hemos ignorado aún...
            if conteo_coords[coord_str] > 1 and coord_str not in coordenadas_ignoradas:
                coordenadas_ignoradas.add(coord_str) # Marcamos que ya ignoramos el primer clon
                continue # Saltamos este primer clon (la "carpeta" del KML)

            # Si es un punto único, o ya es el 2do, 3ro, etc... lo dejamos pasar
            geometrias_filtradas.append(geo)

        # =================================================================

        # 3. Iteramos sobre la lista ya filtrada y perfecta
        for geo in geometrias_filtradas:
            nombre_limpio = geo['nombre'][:255]
            tipo_mapeado = self._mapear_tipo(geo['tipo'])
            
            area_calc = self._calcular_area(geo) if geo['tipo'] == 'Polygon' else None
            perim_calc = self._calcular_perimetro(geo) if geo['tipo'] in ['Polygon', 'LineString'] else None

            geometria_a_actualizar = None

            # Intentamos buscar una coincidencia exacta
            for g in geometrias_existentes:
                if g.nombre == nombre_limpio and g.tipo == tipo_mapeado:
                    geometria_a_actualizar = g
                    break
            
            # Si no hay coincidencia, buscamos una vacía ("fantasma")
            if not geometria_a_actualizar:
                for g in geometrias_existentes:
                    if not g.coordenadas or g.coordenadas == '{}' or g.coordenadas == '':
                        geometria_a_actualizar = g
                        break

            if geometria_a_actualizar:
                # ACTUALIZAMOS
                geometria_a_actualizar.nombre = nombre_limpio
                geometria_a_actualizar.tipo = tipo_mapeado
                geometria_a_actualizar.coordenadas = geo['coordenadas']
                geometria_a_actualizar.propiedades = geo.get('propiedades', {})
                geometria_a_actualizar.area = area_calc
                geometria_a_actualizar.perimetro = perim_calc
                geometria_a_actualizar.save()
                
                geometrias_existentes.remove(geometria_a_actualizar)
                actualizados += 1
                geometria_final = geometria_a_actualizar
            else:
                # CREAMOS NUEVA
                geometria_final = GeometriaEspacial.objects.create(
                    id_archivo=self.archivo_db,
                    nombre=nombre_limpio,
                    tipo=tipo_mapeado,
                    coordenadas=geo['coordenadas'],
                    propiedades=geo.get('propiedades', {}),
                    area=area_calc,
                    perimetro=perim_calc
                )
                creados += 1

            # Auto-crear punto de interés si no existe
            if not geometria_final.punto_interes_set.exists():
                self._crear_punto_interes_automatico(geometria_final, geo)

        return {'creados': creados, 'actualizados': actualizados}
    
    

    def _crear_punto_interes_automatico(self, geometria, geo_dict):
        """
        Analiza las propiedades del KML y crea automáticamente el Punto_Interes
        y su registro específico (Ofrenda, Sitio, etc.)
        """
        nombre_archivo = self.archivo_db.nombre_archivo.lower()
        props = geo_dict.get('propiedades', {})
        
        # 1. Detectar la categoría (Lógica inteligente)
        categoria_detectada = 'otro'
        
        # Si el archivo se llama ofrenda o el KML tiene el campo "Nom_ánima"
        if 'ofrenda' in nombre_archivo or 'Nom_ánima' in props:
            categoria_detectada = 'ofrenda'
        elif 'servicio' in nombre_archivo:
            categoria_detectada = 'servicio'
        elif 'sitio' in nombre_archivo or 'zocalo' in nombre_archivo or 'zócalo' in nombre_archivo:
            categoria_detectada = 'sitio_turistico'

        # 2. Construir una descripción rica extrayendo datos del KML
        descripcion = geo_dict.get('descripcion', '')
        if not descripcion and props:
            detalles = []
            if 'Dirección' in props: 
                detalles.append(f"Dirección: {props['Dirección']}")
            if 'Nom_ánima' in props: 
                detalles.append(f"Dedicada a: {props['Nom_ánima']}")
            
            descripcion = "\n".join(detalles) if detalles else "Importado automáticamente del KML"

        # 3. Crear el Punto_Interes principal
        nuevo_punto = Punto_Interes.objects.create(
            id_geometria=geometria,
            categoria=categoria_detectada,
            nombre=geometria.nombre,
            descripcion=descripcion,
            estado='activo',
            usuario_creacion=self.archivo_db.usuario
        )

        # 4. Crear el registro en la sub-tabla correspondiente
        if categoria_detectada == 'ofrenda':
            # Extraemos el anfitrión (o le ponemos el nombre del ánima por defecto)
            anfitrion = props.get('Nom_ánima') or "Anfitrión Desconocido"
            Ofrenda.objects.create(id_punto=nuevo_punto, anfitrion=anfitrion)
            
        elif categoria_detectada == 'servicio':
            Servicio.objects.create(id_punto=nuevo_punto, tipo_servicio='modulo', contacto="Sin contacto")
            
        elif categoria_detectada == 'sitio_turistico':
            # Buscamos o creamos una categoría genérica para que la base de datos no arroje error
            cat_sitio, created = Categoria_Sitio.objects.get_or_create(
                nombre="Atractivo Importado",
                defaults={'codigo_slug': 'atractivo-importado'}
            )
            Sitio_turistico.objects.create(id_punto=nuevo_punto, id_categoria=cat_sitio, reglas_acceso="")
    
    
    def _mapear_tipo(self, tipo_geojson):
        # ... Tu lógica de mapeo existente ...
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
        # ... Tu lógica de cálculo de área existente ...
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
        # ... Tu lógica de cálculo de perímetro existente ...
        try:
            if geometria['tipo'] == 'Polygon' and geometria['coordenadas']:
                coords = geometria['coordenadas'][0]  # Anillo exterior
            elif geometria['tipo'] == 'LineString':
                coords = geometria['coordenadas']
            else:
                return None
            
            if len(coords) < 2:
                return None
            
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


    def _extraer_propiedades_extendidas(self, placemark):
        # ... Tu lógica de propiedades extendidas existente ...
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

    # ---------------------------------------------------------
    # VERSIÓN CORREGIDA DE EXTRAER GEOMETRÍA
    # ---------------------------------------------------------

# KMLProcessor.py (Reemplaza este método)

    # KMLProcessor.py (Reemplaza este método)

    def _extraer_geometria(self, placemark):
        """
        Extrae TODAS las geometrías de un placemark, manejando MultiGeometry
        y devolviendo siempre una lista de geometrías GeoJSON.
        """
        geometrias_del_placemark = []

        # 1. Intentamos manejar un contenedor MultiGeometry (Múltiples puntos)
        multi = placemark.find('.//kml:MultiGeometry', self.namespace)
        if multi is not None:
            # Llama a la versión corregida de extraer multigeometría (que ahora devuelve lista)
            datos = self._extraer_multigeometria(multi)
            if datos:
                # 'datos' ya es una lista de geometrías, la añadimos a la principal
                geometrias_del_placemark.extend(datos)
        
        # 2. Si es una geometría independiente (no MultiGeometry), la buscamos
        else:
            poligono = placemark.find('.//kml:Polygon', self.namespace)
            if poligono is not None:
                data = self._extraer_poligono(poligono)
                if data: geometrias_del_placemark.append(data)

            linea = placemark.find('.//kml:LineString', self.namespace)
            if linea is not None:
                data = self._extraer_linea(linea)
                if data: geometrias_del_placemark.append(data)

            punto = placemark.find('.//kml:Point', self.namespace)
            if punto is not None:
                data = self._extraer_punto(punto)
                if data: geometrias_del_placemark.append(data)

        # Retorna la lista de geometrías GeoJSON encontradas
        return geometrias_del_placemark if geometrias_del_placemark else None

    # ---------------------------------------------------------
    # VERSIÓN CORREGIDA DE EXTRAER MULTIGEOEMTRÍA
    # ---------------------------------------------------------

# KMLProcessor.py (Reemplaza este método)

# KMLProcessor.py (Reemplaza este método)

    # KMLProcessor.py (Reemplaza este método)

    def _extraer_multigeometria(self, multi_elem):
        """
        Extrae TODAS las geometrías válidas de un contenedor MultiGeometry.
        Devuelve una lista de diccionarios de geometría GeoJSON.
        """
        geometrias_encontradas = []

        # Buscamos TODOS los puntos dentro de la multigeometría
        for punto in multi_elem.findall('.//kml:Point', self.namespace):
            data = self._extraer_punto(punto)
            if data: geometrias_encontradas.append(data)

        # Buscamos TODAS las líneas dentro de la multigeometría
        for linea in multi_elem.findall('.//kml:LineString', self.namespace):
            data = self._extraer_linea(linea)
            if data: geometrias_encontradas.append(data)

        # Buscamos TODOS los polígonos dentro de la multigeometría
        for poligono in multi_elem.findall('.//kml:Polygon', self.namespace):
            data = self._extraer_poligono(poligono)
            if data: geometrias_encontradas.append(data)

        return geometrias_encontradas if geometrias_encontradas else None

    def _extraer_punto(self, punto_elem):
        # ... Tu lógica de extracción de punto existente ...
        coords_elem = punto_elem.find('.//kml:coordinates', self.namespace)
        if coords_elem is None or not coords_elem.text: 
            return None
        
        # Limpiamos todo tipo de basura: espacios, saltos de línea y tabuladores
        coords_text = coords_elem.text.strip()
        
        # El KML puede separar por espacios o comas.
        partes = [p.strip() for p in coords_text.split(',') if p.strip()]
        
        if len(partes) >= 2:
            try:
                # En KML el orden es siempre Longitud, Latitud, [Altitud]
                lon = float(partes[0])
                lat = float(partes[1])
                return {'tipo': 'Point', 'coordenadas': [lon, lat]}
            except (ValueError, IndexError):
                return None
        return None

    def _extraer_linea(self, linea_elem):
        # ... Tu lógica de extracción de línea existente ...
        coords_elem = linea_elem.find('.//kml:coordinates', self.namespace)
        if coords_elem is None or not coords_elem.text: 
            return None
        
        coordenadas = []
        # Separamos por espacios para obtener cada punto de la línea
        puntos_texto = coords_elem.text.strip().split()
        
        for p in puntos_texto:
            partes = p.split(',')
            if len(partes) >= 2:
                try:
                    coordenadas.append([float(partes[0]), float(partes[1])])
                except ValueError:
                    continue
        
        if len(coordenadas) >= 2:
            return {'tipo': 'LineString', 'coordenadas': coordenadas}
        return None

    def _extraer_poligono(self, poligono_elem):
        # ... Tu lógica de extracción de polígono existente ...
        anillo = poligono_elem.find('.//kml:outerBoundaryIs/kml:LinearRing', self.namespace)
        if anillo is None: 
            return None
        
        coords_elem = anillo.find('.//kml:coordinates', self.namespace)
        if coords_elem is None or not coords_elem.text: 
            return None
        
        coordenadas = []
        # Separamos por espacios para obtener cada punto del polígono
        for coord_line in coords_elem.text.strip().split():
            coords = coord_line.split(',')
            if len(coords) >= 2:
                try:
                    lon = float(coords[0])
                    lat = float(coords[1])
                    coordenadas.append([lon, lat])
                except ValueError:
                    continue
        
        if len(coordenadas) >= 3:  # Un polígono necesita al menos 3 puntos
            # El GeoJSON para un Polygon es una lista de listas (anillos)
            return {'tipo': 'Polygon', 'coordenadas': [coordenadas]}
        return None