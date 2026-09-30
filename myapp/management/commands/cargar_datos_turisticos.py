import json
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from myapp.models import (
    Usuario, ArchivoKMZ, GeometriaEspacial, Categoria_Sitio,
    Punto_Interes, Sitio_turistico, Ofrenda, Servicio
)


class Command(BaseCommand):
    help = 'Puebla la base de datos con los sitios históricos, ofrendas monumentales y servicios turísticos de Huaquechula'

    def handle(self, *args, **options):
        self.stdout.write("Iniciando carga de datos turísticos de Huaquechula...")

        # 1. Obtener o crear usuario admin para atribución
        admin_user = Usuario.objects.filter(is_superuser=True).first()
        if not admin_user:
            admin_user = Usuario.objects.filter(tipo='admin').first()
        if not admin_user:
            admin_user = Usuario.objects.create(
                nombre_usuario='admin_huaquechula',
                email='admin@huaquechula.gob.mx',
                nombre='Administrador',
                ap='Huaquechula',
                tipo='admin',
                is_staff=True,
                is_superuser=True,
                is_active=True
            )
            admin_user.set_password('Admin#2026Huaquechula!')
            admin_user.save()

        with transaction.atomic():
            # 2. Categorías de Sitios Turísticos
            cat_religioso, _ = Categoria_Sitio.objects.get_or_create(
                nombre="Patrimonio Religioso",
                defaults={"codigo_slug": "patrimonio-religioso"}
            )
            cat_historico, _ = Categoria_Sitio.objects.get_or_create(
                nombre="Atractivo Histórico",
                defaults={"codigo_slug": "atractivo-historico"}
            )
            cat_plazas, _ = Categoria_Sitio.objects.get_or_create(
                nombre="Plazas y Espacios Públicos",
                defaults={"codigo_slug": "plazas-y-espacios-publicos"}
            )
            cat_gastronomia, _ = Categoria_Sitio.objects.get_or_create(
                nombre="Gastronomía y Tradición",
                defaults={"codigo_slug": "gastronomia-y-tradicion"}
            )

            # 3. Archivo KMZ maestro de catálogo
            archivo_kmz, _ = ArchivoKMZ.objects.get_or_create(
                nombre_archivo="Catalogo_Turistico_Huaquechula.kml",
                defaults={
                    "usuario": admin_user,
                    "archivo_path": "media/kmz_files/Catalogo_Turistico_Huaquechula.kml",
                    "tipo_archivo": "kml",
                    "visible": True,
                    "procesado": True,
                    "descripcion": "Catálogo oficial de sitios patrimoniales, ofrendas monumentales y servicios"
                }
            )

            # 4. Datos Maestros de Puntos de Interés
            # Formato: [nombre, categoria, lat, lng, extra_data, descripcion, horario]
            puntos_maestros = [
                # Sitios Históricos y Templos
                {
                    "nombre": "Ex-Convento de San Francisco",
                    "categoria": "sitio_turistico",
                    "cat_sitio": cat_religioso,
                    "lat": 18.770173,
                    "lng": -98.541134,
                    "descripcion": "Monumento histórico del siglo XVI, joya arquitectónica del virreinato con claustro, pintura mural y fachada plateresca.",
                    "horario": "09:00 - 18:00",
                    "imagen": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e7/Ex_Convento_de_San_Francisco_en_Huaquechula.jpg/800px-Ex_Convento_de_San_Francisco_en_Huaquechula.jpg"
                },
                {
                    "nombre": "Parroquia de San Martín Obispo de Tours",
                    "categoria": "sitio_turistico",
                    "cat_sitio": cat_religioso,
                    "lat": 18.770183,
                    "lng": -98.542552,
                    "descripcion": "Templo parroquial de gran tradición devocional en el corazón de Huaquechula, con altares barrocos y retablos dorados.",
                    "horario": "08:00 - 19:00",
                    "imagen": ""
                },
                {
                    "nombre": "Capilla de San José",
                    "categoria": "sitio_turistico",
                    "cat_sitio": cat_religioso,
                    "lat": 18.768481,
                    "lng": -98.541395,
                    "descripcion": "Capilla de barrio tradicional, testimonio de la fe comunitaria y punto neurálgico en procesiones y festividades.",
                    "horario": "09:00 - 17:00",
                    "imagen": ""
                },
                {
                    "nombre": "Zócalo de Huaquechula",
                    "categoria": "sitio_turistico",
                    "cat_sitio": cat_plazas,
                    "lat": 18.769895,
                    "lng": -98.544040,
                    "descripcion": "Plaza Principal con quiosco tradicional, jardines sombreados, Palacio Municipal y punto de encuentro cívico y cultural.",
                    "horario": "Abierto 24 horas",
                    "imagen": ""
                },
                # Ofrendas Monumentales Tradicionales (Patrimonio Cultural Inmaterial)
                {
                    "nombre": "Ofrenda Monumental Familia Soriano",
                    "categoria": "ofrenda",
                    "anfitrion": "Don Manuel Soriano",
                    "lat": 18.769400,
                    "lng": -98.543500,
                    "descripcion": "Altar monumental piramidal de 3 niveles revestido en tela de raso blanco, adornado con ángeles de pasta y cera escamada.",
                    "horario": "10:00 - 22:00",
                    "imagen": ""
                },
                {
                    "nombre": "Ofrenda Monumental Familia Domínguez",
                    "categoria": "ofrenda",
                    "anfitrion": "Doña Carmen Domínguez",
                    "lat": 18.771100,
                    "lng": -98.544800,
                    "descripcion": "Ofrenda tradicional dedicada a 'ánima nueva', con chocolate de agua, hojaldras de manteca y candeleros de barro vidriado.",
                    "horario": "10:00 - 22:00",
                    "imagen": ""
                },
                {
                    "nombre": "Ofrenda Monumental Familia Flores Pérez",
                    "categoria": "ofrenda",
                    "anfitrion": "Familia Flores Pérez",
                    "lat": 18.768900,
                    "lng": -98.545200,
                    "descripcion": "Espectacular estructura de raso blanco iluminada con velas y sahumerios de copal, conservando la tradición de más de 4 siglos.",
                    "horario": "10:00 - 22:00",
                    "imagen": ""
                },
                {
                    "nombre": "Ofrenda Monumental Los Cuatro Vientos",
                    "categoria": "ofrenda",
                    "anfitrion": "Colectivo Cultural Huaquechula",
                    "lat": 18.771900,
                    "lng": -98.542700,
                    "descripcion": "Altar que entrelaza la cosmovisión prehispánica con la iconografía virreinal, rodeado de alfombra de flor de cempasúchil.",
                    "horario": "10:00 - 21:00",
                    "imagen": ""
                },
                {
                    "nombre": "Ofrenda Monumental Capilla La Purísima",
                    "categoria": "ofrenda",
                    "anfitrion": "Mayordomía de Barrio",
                    "lat": 18.770700,
                    "lng": -98.546100,
                    "descripcion": "Altar comunitario erigido por los mayordomos en honor a las ánimas benditas del purgatorio, con figuras místicas en azúcar.",
                    "horario": "10:00 - 22:00",
                    "imagen": ""
                },
                # Servicios Turísticos
                {
                    "nombre": "Cajero Automático Banorte",
                    "categoria": "servicio",
                    "tipo_servicio": "cajero",
                    "contacto": "Red de Cajeros Nacionales",
                    "lat": 18.769100,
                    "lng": -98.541451,
                    "descripcion": "Cajero automático disponible las 24 horas para retiro de efectivo y operaciones de visitantes.",
                    "horario": "24 horas",
                    "imagen": ""
                },
                {
                    "nombre": "Módulo de Información Turística Zócalo",
                    "categoria": "servicio",
                    "tipo_servicio": "modulo",
                    "contacto": "Turismo Municipal: (244) 445-1234",
                    "lat": 18.769950,
                    "lng": -98.544100,
                    "descripcion": "Atención personalizada al visitante, mapas físicos de ofrendas monumentales y guías comunitarios.",
                    "horario": "09:00 - 18:00",
                    "imagen": ""
                }
            ]

            total_creados = 0
            for item in puntos_maestros:
                # 1. Geometría Espacial
                geo_coords = [item["lng"], item["lat"]]
                geo, _ = GeometriaEspacial.objects.get_or_create(
                    id_archivo=archivo_kmz,
                    nombre=item["nombre"],
                    defaults={
                        "tipo": "punto",
                        "coordenadas": geo_coords,
                        "propiedades": {"nombre": item["nombre"], "categoria": item["categoria"]}
                    }
                )

                # Asegurar coordenadas correctas si ya existía
                geo.coordenadas = geo_coords
                geo.tipo = "punto"
                geo.save()

                # 2. Punto de Interés
                pto, creado = Punto_Interes.objects.get_or_create(
                    id_geometria=geo,
                    defaults={
                        "nombre": item["nombre"],
                        "categoria": item["categoria"],
                        "descripcion": item["descripcion"],
                        "estado": "activo",
                        "imagen_portada": item.get("imagen") or None,
                        "usuario_creacion": admin_user,
                        "hora_apertura": "09:00:00" if "09:00" in item.get("horario", "") else None,
                        "hora_cierre": "18:00:00" if "18:00" in item.get("horario", "") else None,
                    }
                )

                # Si ya existía, asegurar estado activo y categoría
                pto.nombre = item["nombre"]
                pto.categoria = item["categoria"]
                pto.estado = "activo"
                pto.descripcion = item["descripcion"]
                if item.get("imagen"):
                    pto.imagen_portada = item["imagen"]
                pto.save()

                # 3. Sub-tabla según categoría
                if item["categoria"] == "ofrenda":
                    Ofrenda.objects.update_or_create(
                        id_punto=pto,
                        defaults={"anfitrion": item.get("anfitrion", "Anfitrión Tradicional")}
                    )
                elif item["categoria"] == "sitio_turistico":
                    Sitio_turistico.objects.update_or_create(
                        id_punto=pto,
                        defaults={
                            "id_categoria": item.get("cat_sitio") or cat_historico,
                            "reglas_acceso": "Respetar el silencio en templos y no tocar las piezas de arte sacro."
                        }
                    )
                elif item["categoria"] == "servicio":
                    Servicio.objects.update_or_create(
                        id_punto=pto,
                        defaults={
                            "tipo_servicio": item.get("tipo_servicio", "modulo"),
                            "contacto": item.get("contacto", "Módulo de Atención")
                        }
                    )

                total_creados += 1
                self.stdout.write(self.style.SUCCESS(f"  ✓ [{item['categoria'].upper()}] {item['nombre']} listo."))

            self.stdout.write(self.style.SUCCESS(f"\n¡Éxito! Se cargaron/actualizaron {total_creados} puntos de interés y geometrías espaciales."))
