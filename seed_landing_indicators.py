import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from myapp.models import Eje, CategoriaIndicador, Indicador

print("=== Creando/Obteniendo Eje 'Indicadores del evento' ===")
eje_landing, created = Eje.objects.get_or_create(
    nombre="Indicadores del evento",
    defaults={"descripcion": "Eje de visualizaciones de la página principal (Landing Page)"}
)
if created:
    print("- Eje 'Indicadores del evento' creado con éxito.")
else:
    print("- Eje 'Indicadores del evento' ya existía.")

# Definición de indicadores por categoría
indicadores_data = {
    "Kpis Principales": [
        {
            "nombre": "Afluencia durante la tradicion",
            "descripcion": "Número de visitantes registrados al municipio durante la tradición (temporada de festividades)",
            "unidad_medida": "Visitantes",
            "data_source": "encuesta",
            "encuesta_tipo": "institucional",
            "encuesta_pregunta": "Pregunta 3"
        },
        {
            "nombre": "Visitantes anuales",
            "descripcion": "Número de visitantes registrados al municipio durante el año",
            "unidad_medida": "Visitantes",
            "data_source": "encuesta",
            "encuesta_tipo": "institucional",
            "encuesta_pregunta": "Pregunta 7"
        },
        {
            "nombre": "Indice de satisfaccion",
            "descripcion": "Índice de satisfacción promedio de los visitantes",
            "unidad_medida": "Porcentaje/Puntos",
            "data_source": "encuesta",
            "encuesta_tipo": "visitante",
            "encuesta_pregunta": "Pregunta 7"
        }
    ],
    "Origen y conectividad": [
        {
            "nombre": "Afluencia por zonas",
            "descripcion": "Afluencia de visitantes por zonas del municipio",
            "unidad_medida": "Zonas",
            "data_source": "encuesta",
            "encuesta_tipo": "visitante",
            "encuesta_pregunta": "Pregunta 5"
        },
        {
            "nombre": "Visitas por ciudad",
            "descripcion": "Ciudades de residencia habitual de los visitantes",
            "unidad_medida": "Ciudades",
            "data_source": "encuesta",
            "encuesta_tipo": "visitante",
            "encuesta_pregunta": "Pregunta 4"
        }
    ],
    "Perfil demográfico del visitante": [
        {
            "nombre": "Perfil del visitante",
            "descripcion": "Edad promedio y distribución de género de los visitantes",
            "unidad_medida": "Demografía",
            "data_source": "encuesta",
            "encuesta_tipo": "visitante",
            "encuesta_pregunta": "Pregunta 1 y 2"
        },
        {
            "nombre": "Grupo de visita",
            "descripcion": "Acompañantes en el viaje del visitante (pareja, familia, solo, etc.)",
            "unidad_medida": "Grupos",
            "data_source": "encuesta",
            "encuesta_tipo": "visitante",
            "encuesta_pregunta": "Pregunta 3"
        }
    ],
    "Comportamiento en la tradición": [
        {
            "nombre": "Actividades populares",
            "descripcion": "Actividades o atractivos preferidos durante las festividades",
            "unidad_medida": "Actividades",
            "data_source": "encuesta",
            "encuesta_tipo": "visitante",
            "encuesta_pregunta": "Pregunta 6"
        },
        {
            "nombre": "Resenas",
            "descripcion": "Reseñas, opiniones o comentarios recopilados del visitante",
            "unidad_medida": "Reseñas",
            "data_source": "encuesta",
            "encuesta_tipo": "visitante",
            "encuesta_pregunta": "Pregunta 8"
        }
    ]
}

print("\n=== Creando Categorías e Indicadores ===")
for cat_nombre, inds in indicadores_data.items():
    cat, cat_created = CategoriaIndicador.objects.get_or_create(
        eje=eje_landing,
        nombre=cat_nombre
    )
    if cat_created:
        print(f"\nCategoría '{cat_nombre}' creada.")
    else:
        print(f"\nCategoría '{cat_nombre}' ya existía.")
        
    for ind_info in inds:
        ind, ind_created = Indicador.objects.get_or_create(
            categoria=cat,
            nombre=ind_info["nombre"],
            defaults={
                "descripcion": ind_info["descripcion"],
                "unidad_medida": ind_info["unidad_medida"],
                "data_source": ind_info["data_source"],
                "encuesta_tipo": ind_info["encuesta_tipo"],
                "encuesta_pregunta": ind_info["encuesta_pregunta"]
            }
        )
        if ind_created:
            print(f"  - Indicador '{ind.nombre}' creado.")
        else:
            # Asegurar que los campos estén actualizados
            ind.descripcion = ind_info["descripcion"]
            ind.unidad_medida = ind_info["unidad_medida"]
            ind.data_source = ind_info["data_source"]
            ind.encuesta_tipo = ind_info["encuesta_tipo"]
            ind.encuesta_pregunta = ind_info["encuesta_pregunta"]
            ind.save()
            print(f"  - Indicador '{ind.nombre}' ya existía (campos sincronizados).")

print("\n=== Proceso de Inicialización Completado ===")
