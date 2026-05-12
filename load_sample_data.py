
import os
import django
import sys

# Setup Django environment
sys.path.append(r'c:\Users\BORRE117\Downloads\Prueba AntiG\Observatorio-de-Datos-Huaquechula')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from myapp.models import Eje, CategoriaIndicador, Indicador, Medicion
from django.contrib.auth.models import User
from myapp.models import Usuario

def load_data():
    print("Creating sample data...")
    
    # 1. Create Ejes
    eje_social, _ = Eje.objects.get_or_create(nombre="Bienestar Social", descripcion="Indicadores de salud, educación y vivienda")
    eje_tradicion, _ = Eje.objects.get_or_create(nombre="Tradición y Patrimonio", descripcion="Preservación cultural y tensiones")
    eje_turismo, _ = Eje.objects.get_or_create(nombre="Turismo Comunitario", descripcion="Impacto y gestión turística")

    # 2. Create Categories
    cat_salud, _ = CategoriaIndicador.objects.get_or_create(eje=eje_social, nombre="Salud")
    cat_accesibilidad_servicios, _ = CategoriaIndicador.objects.get_or_create(eje=eje_social, nombre="Accesibilidad a servicios")
    cat_educacion, _ = CategoriaIndicador.objects.get_or_create(eje=eje_social, nombre="Educación")
    cat_vivienda, _ = CategoriaIndicador.objects.get_or_create(eje=eje_social, nombre="Vivienda")
    cat_ingresos, _ = CategoriaIndicador.objects.get_or_create(eje=eje_social, nombre="Ingresos")
    cat_empleo, _ = CategoriaIndicador.objects.get_or_create(eje=eje_social, nombre="Empleo")
    cat_seguridad, _ = CategoriaIndicador.objects.get_or_create(eje=eje_social, nombre="Seguridad")
    cat_medio_ambiente, _ = CategoriaIndicador.objects.get_or_create(eje=eje_social, nombre="Medio Ambiente")
    cat_migracion, _ = CategoriaIndicador.objects.get_or_create(eje=eje_social, nombre="Migración")

    cat_pci, _ = CategoriaIndicador.objects.get_or_create(eje=eje_tradicion, nombre="Tensión sobre la comunidad y el Patrimonio Cultural Inmaterial PCI")
    cat_salvaguardia, _ = CategoriaIndicador.objects.get_or_create(eje=eje_tradicion, nombre="Salvaguardia")

    cat_participacion_gobernanza, _ = CategoriaIndicador.objects.get_or_create(eje=eje_turismo, nombre="Participación y gobernanza en el turismo")
    cat_gestion, _ = CategoriaIndicador.objects.get_or_create(eje=eje_turismo, nombre="Gestión del turismo")

    # 3. Create Indicators - Salud
    ind_esp_vida, _ = Indicador.objects.get_or_create(
        categoria=cat_salud, 
        nombre="Esperanza de vida al nacer", 
        unidad_medida="Años"
    )
    ind_salud_auto, _ = Indicador.objects.get_or_create(
        categoria=cat_salud, 
        nombre="Salud auto reportada", 
        unidad_medida="Porcentaje"
    )
    ind_obesidad, _ = Indicador.objects.get_or_create(
        categoria=cat_salud, 
        nombre="Tasa de obesidad", 
        unidad_medida="Porcentaje"
    )
    ind_mortalidad, _ = Indicador.objects.get_or_create(
        categoria=cat_salud, 
        nombre="Tasa de mortalidad", 
        unidad_medida="Por mil"
    )
    ind_mort_materna, _ = Indicador.objects.get_or_create(
        categoria=cat_salud, 
        nombre="Razón de mortalidad materna", 
        unidad_medida="Por 100,000"
    )
    
    # Accesibilidad a servicios
    ind_acceso_salud, _ = Indicador.objects.get_or_create(
        categoria=cat_accesibilidad_servicios,
        nombre="Acceso a servicios de salud",
        unidad_medida="Porcentaje"
    )
    ind_banda_ancha, _ = Indicador.objects.get_or_create(
        categoria=cat_accesibilidad_servicios,
        nombre="Acceso a los servicios de banda ancha",
        unidad_medida="Porcentaje"
    )
    ind_servicios_basicos, _ = Indicador.objects.get_or_create(
        categoria=cat_accesibilidad_servicios,
        nombre="Vivienda con acceso de servicios básicos",
        unidad_medida="Porcentaje"
    )
    
    # Educación
    ind_niveles_educacion, _ = Indicador.objects.get_or_create(
        categoria=cat_educacion,
        nombre="Niveles de educación",
        unidad_medida="Porcentaje"
    )
    ind_desercion_escolar, _ = Indicador.objects.get_or_create(
        categoria=cat_educacion,
        nombre="Deserción escolar",
        unidad_medida="Porcentaje"
    )
    ind_anios_escolaridad, _ = Indicador.objects.get_or_create(
        categoria=cat_educacion,
        nombre="Años promedio de escolaridad",
        unidad_medida="Años"
    )
    
    # Vivienda
    ind_habitaciones_persona, _ = Indicador.objects.get_or_create(
        categoria=cat_vivienda,
        nombre="Habitaciones por persona",
        unidad_medida="Promedio"
    )
    ind_techos_resistentes, _ = Indicador.objects.get_or_create(
        categoria=cat_vivienda,
        nombre="Viviendas con techos de materiales resistentes",
        unidad_medida="Porcentaje"
    )
    
    # Ingresos
    ind_gini, _ = Indicador.objects.get_or_create(
        categoria=cat_ingresos,
        nombre="Gini del ingreso disponible de los hogares per cápita",
        unidad_medida="Índice"
    )
    ind_ingreso_equiv, _ = Indicador.objects.get_or_create(
        categoria=cat_ingresos,
        nombre="Ingreso equivalente disponible de los hogares",
        unidad_medida="Pesos"
    )
    ind_pobreza_ingresos, _ = Indicador.objects.get_or_create(
        categoria=cat_ingresos,
        nombre="Población en pobreza",
        unidad_medida="Personas"
    )
    ind_pobreza_extrema, _ = Indicador.objects.get_or_create(
        categoria=cat_ingresos,
        nombre="Población en pobreza extrema",
        unidad_medida="Personas"
    )
    
    # Empleo
    ind_condiciones_criticas, _ = Indicador.objects.get_or_create(
        categoria=cat_empleo,
        nombre="Tasa de condiciones críticas de ocupación",
        unidad_medida="Porcentaje"
    )
    ind_informalidad, _ = Indicador.objects.get_or_create(
        categoria=cat_empleo,
        nombre="Informalidad laboral",
        unidad_medida="Porcentaje"
    )
    ind_desocupacion, _ = Indicador.objects.get_or_create(
        categoria=cat_empleo,
        nombre="Tasa de desocupación",
        unidad_medida="Porcentaje"
    )
    ind_participacion_econ, _ = Indicador.objects.get_or_create(
        categoria=cat_empleo,
        nombre="Participación económica",
        unidad_medida="Porcentaje"
    )
    
    # Seguridad
    ind_homicidios, _ = Indicador.objects.get_or_create(
        categoria=cat_seguridad,
        nombre="Tasa de homicidios",
        unidad_medida="Por 100,000"
    )
    ind_confianza_policia, _ = Indicador.objects.get_or_create(
        categoria=cat_seguridad,
        nombre="Confianza policía",
        unidad_medida="Porcentaje"
    )
    ind_percepcion_inseguridad, _ = Indicador.objects.get_or_create(
        categoria=cat_seguridad,
        nombre="Percepción de inseguridad",
        unidad_medida="Porcentaje"
    )
    ind_incidencia_delictiva, _ = Indicador.objects.get_or_create(
        categoria=cat_seguridad,
        nombre="Incidencia delictiva",
        unidad_medida="Por 100,000"
    )
    
    # Medio ambiente
    ind_contaminacion_aire, _ = Indicador.objects.get_or_create(
        categoria=cat_medio_ambiente,
        nombre="Contaminación del aire",
        unidad_medida="PM2.5"
    )
    ind_disposicion_residuos, _ = Indicador.objects.get_or_create(
        categoria=cat_medio_ambiente,
        nombre="Disposición de residuos",
        unidad_medida="Porcentaje"
    )
    ind_gestion_ambiental, _ = Indicador.objects.get_or_create(
        categoria=cat_medio_ambiente,
        nombre="Alternativas de gestión comunitaria de medio ambiente",
        unidad_medida="Cantidad"
    )
    
    # Migración
    ind_intensidad_migratoria, _ = Indicador.objects.get_or_create(
        categoria=cat_migracion,
        nombre="Índice de intensidad migratoria",
        unidad_medida="Índice"
    )
    
    # Tradición y Patrimonio - PCI
    ind_tension_poblacion, _ = Indicador.objects.get_or_create(
        categoria=cat_pci,
        nombre="Tensión sobre la población local",
        unidad_medida="Índice"
    )
    ind_acceso_servicios_tradicion, _ = Indicador.objects.get_or_create(
        categoria=cat_pci,
        nombre="Acceso de la población a los servicios públicos durante la tradición",
        unidad_medida="Porcentaje"
    )
    ind_tensiones_fisicas, _ = Indicador.objects.get_or_create(
        categoria=cat_pci,
        nombre="Tensiones físicas y simbólicas sobre la tradición",
        unidad_medida="Índice"
    )
    
    # Tradición y Patrimonio - Salvaguardia
    ind_procesos_salvaguardia, _ = Indicador.objects.get_or_create(
        categoria=cat_salvaguardia,
        nombre="Procesos de salvaguardia del Patrimonio",
        unidad_medida="Cantidad"
    )
    ind_seguimiento_salvaguardia, _ = Indicador.objects.get_or_create(
        categoria=cat_salvaguardia,
        nombre="Seguimiento de salvaguardia",
        unidad_medida="Índice"
    )
    ind_difusion_pci, _ = Indicador.objects.get_or_create(
        categoria=cat_salvaguardia,
        nombre="Difusión de PCI",
        unidad_medida="Cantidad"
    )
    ind_relacion_comunidad_pci, _ = Indicador.objects.get_or_create(
        categoria=cat_salvaguardia,
        nombre="Relación comunidad - PCI",
        unidad_medida="Índice"
    )
    
    # Turismo Comunitario - Participación y gobernanza
    ind_participacion_decisiones, _ = Indicador.objects.get_or_create(
        categoria=cat_participacion_gobernanza,
        nombre="Participación de la comunidad en la toma de decisiones",
        unidad_medida="Porcentaje"
    )
    ind_capacitacion_info, _ = Indicador.objects.get_or_create(
        categoria=cat_participacion_gobernanza,
        nombre="Capacitación, información y comunicación",
        unidad_medida="Índice"
    )
    ind_regulacion, _ = Indicador.objects.get_or_create(
        categoria=cat_participacion_gobernanza,
        nombre="Regulación",
        unidad_medida="Índice"
    )
    
    # Turismo Comunitario - Gestión del turismo
    ind_herramientas_gestion, _ = Indicador.objects.get_or_create(
        categoria=cat_gestion,
        nombre="Herramientas de gestión",
        unidad_medida="Cantidad"
    )
    ind_proyectos_turisticos, _ = Indicador.objects.get_or_create(
        categoria=cat_gestion,
        nombre="Proyectos turísticos",
        unidad_medida="Cantidad"
    )
    ind_integracion_territorial, _ = Indicador.objects.get_or_create(
        categoria=cat_gestion,
        nombre="Integración turística territorial",
        unidad_medida="Índice"
    )

    # 4. Create Measurements — Multi-year data (2020-2024) for trends & sparklines
    # Helper to bulk-create measurements for multiple periods
    def create_multi_year(indicador, data_by_year):
        """data_by_year: dict like {'2020': 73.2, '2021': 74.0, ...}"""
        for periodo, valor in data_by_year.items():
            Medicion.objects.get_or_create(
                indicador=indicador, periodo=periodo, defaults={'valor': valor}
            )

    # ── Salud ──────────────────────────────────────────
    create_multi_year(ind_esp_vida, {
        '2020': 73.2, '2021': 73.8, '2022': 74.5, '2023': 75.5, '2024': 75.9
    })
    create_multi_year(ind_salud_auto, {
        '2020': 62.5, '2021': 64.1, '2022': 66.0, '2023': 68.2, '2024': 69.8
    })
    create_multi_year(ind_obesidad, {
        '2020': 30.1, '2021': 31.2, '2022': 32.5, '2023': 33.4, '2024': 34.0
    })
    create_multi_year(ind_mortalidad, {
        '2020': 6.5, '2021': 7.2, '2022': 6.1, '2023': 5.8, '2024': 5.5
    })
    create_multi_year(ind_mort_materna, {
        '2020': 42.0, '2021': 39.5, '2022': 37.0, '2023': 34.5, '2024': 32.8
    })

    # ── Accesibilidad a servicios ──────────────────────
    create_multi_year(ind_acceso_salud, {
        '2020': 74.5, '2021': 76.8, '2022': 79.2, '2023': 82.3, '2024': 84.1
    })
    create_multi_year(ind_banda_ancha, {
        '2020': 38.2, '2021': 42.5, '2022': 48.3, '2023': 56.7, '2024': 62.4
    })
    create_multi_year(ind_servicios_basicos, {
        '2020': 85.3, '2021': 87.1, '2022': 89.0, '2023': 91.2, '2024': 92.8
    })

    # ── Educación ──────────────────────────────────────
    create_multi_year(ind_niveles_educacion, {
        '2020': 40.2, '2021': 41.8, '2022': 43.5, '2023': 45.8, '2024': 47.3
    })
    create_multi_year(ind_desercion_escolar, {
        '2020': 11.5, '2021': 10.8, '2022': 9.6, '2023': 8.3, '2024': 7.5
    })
    create_multi_year(ind_anios_escolaridad, {
        '2020': 8.2, '2021': 8.5, '2022': 8.8, '2023': 9.2, '2024': 9.5
    })

    # ── Vivienda ───────────────────────────────────────
    create_multi_year(ind_habitaciones_persona, {
        '2020': 1.0, '2021': 1.05, '2022': 1.1, '2023': 1.2, '2024': 1.25
    })
    create_multi_year(ind_techos_resistentes, {
        '2020': 80.2, '2021': 82.5, '2022': 84.8, '2023': 87.5, '2024': 89.3
    })

    # ── Ingresos ───────────────────────────────────────
    create_multi_year(ind_gini, {
        '2020': 0.46, '2021': 0.45, '2022': 0.44, '2023': 0.42, '2024': 0.41
    })
    create_multi_year(ind_ingreso_equiv, {
        '2020': 6800.00, '2021': 7200.00, '2022': 7850.00, '2023': 8750.50, '2024': 9200.00
    })
    create_multi_year(ind_pobreza_ingresos, {
        '2020': 15200, '2021': 14500, '2022': 13600, '2023': 12500, '2024': 11800
    })
    create_multi_year(ind_pobreza_extrema, {
        '2020': 4500, '2021': 4100, '2022': 3700, '2023': 3200, '2024': 2900
    })

    # ── Empleo ─────────────────────────────────────────
    create_multi_year(ind_condiciones_criticas, {
        '2020': 16.5, '2021': 15.2, '2022': 14.0, '2023': 12.8, '2024': 11.5
    })
    create_multi_year(ind_informalidad, {
        '2020': 62.5, '2021': 60.8, '2022': 58.5, '2023': 56.3, '2024': 54.2
    })
    create_multi_year(ind_desocupacion, {
        '2020': 5.2, '2021': 4.8, '2022': 4.1, '2023': 3.5, '2024': 3.2
    })
    create_multi_year(ind_participacion_econ, {
        '2020': 52.3, '2021': 54.1, '2022': 56.5, '2023': 58.7, '2024': 60.2
    })

    # ── Seguridad ──────────────────────────────────────
    create_multi_year(ind_homicidios, {
        '2020': 18.5, '2021': 17.2, '2022': 16.1, '2023': 15.2, '2024': 14.0
    })
    create_multi_year(ind_confianza_policia, {
        '2020': 35.2, '2021': 37.5, '2022': 39.8, '2023': 42.5, '2024': 45.0
    })
    create_multi_year(ind_percepcion_inseguridad, {
        '2020': 78.5, '2021': 75.2, '2022': 72.0, '2023': 68.9, '2024': 66.3
    })
    create_multi_year(ind_incidencia_delictiva, {
        '2020': 410.0, '2021': 385.5, '2022': 350.2, '2023': 320.5, '2024': 298.0
    })

    # ── Medio ambiente ─────────────────────────────────
    create_multi_year(ind_contaminacion_aire, {
        '2020': 32.5, '2021': 31.0, '2022': 29.8, '2023': 28.3, '2024': 27.1
    })
    create_multi_year(ind_disposicion_residuos, {
        '2020': 68.5, '2021': 71.2, '2022': 74.8, '2023': 78.5, '2024': 81.3
    })
    create_multi_year(ind_gestion_ambiental, {
        '2020': 2, '2021': 3, '2022': 3, '2023': 5, '2024': 6
    })

    # ── Migración ──────────────────────────────────────
    create_multi_year(ind_intensidad_migratoria, {
        '2020': 2.3, '2021': 2.1, '2022': 2.0, '2023': 1.8, '2024': 1.7
    })

    # ── Tradición y Patrimonio — PCI ───────────────────
    create_multi_year(ind_tension_poblacion, {
        '2020': 3.1, '2021': 2.8, '2022': 2.6, '2023': 2.3, '2024': 2.1
    })
    create_multi_year(ind_acceso_servicios_tradicion, {
        '2020': 55.0, '2021': 58.2, '2022': 61.5, '2023': 65.4, '2024': 68.0
    })
    create_multi_year(ind_tensiones_fisicas, {
        '2020': 2.5, '2021': 2.3, '2022': 2.0, '2023': 1.8, '2024': 1.6
    })

    # ── Tradición y Patrimonio — Salvaguardia ──────────
    create_multi_year(ind_procesos_salvaguardia, {
        '2020': 1, '2021': 2, '2022': 2, '2023': 3, '2024': 4
    })
    create_multi_year(ind_seguimiento_salvaguardia, {
        '2020': 1.5, '2021': 1.8, '2022': 2.1, '2023': 2.5, '2024': 2.9
    })
    create_multi_year(ind_difusion_pci, {
        '2020': 4, '2021': 5, '2022': 6, '2023': 8, '2024': 10
    })
    create_multi_year(ind_relacion_comunidad_pci, {
        '2020': 2.2, '2021': 2.5, '2022': 2.8, '2023': 3.2, '2024': 3.5
    })

    # ── Turismo Comunitario — Participación y gobernanza
    create_multi_year(ind_participacion_decisiones, {
        '2020': 32.0, '2021': 36.5, '2022': 40.8, '2023': 45.3, '2024': 49.0
    })
    create_multi_year(ind_capacitacion_info, {
        '2020': 1.5, '2021': 1.8, '2022': 2.2, '2023': 2.8, '2024': 3.2
    })
    create_multi_year(ind_regulacion, {
        '2020': 1.2, '2021': 1.5, '2022': 1.8, '2023': 2.1, '2024': 2.5
    })

    # ── Turismo Comunitario — Gestión del turismo ──────
    create_multi_year(ind_herramientas_gestion, {
        '2020': 2, '2021': 2, '2022': 3, '2023': 4, '2024': 5
    })
    create_multi_year(ind_proyectos_turisticos, {
        '2020': 3, '2021': 4, '2022': 4, '2023': 6, '2024': 7
    })
    create_multi_year(ind_integracion_territorial, {
        '2020': 1.5, '2021': 1.8, '2022': 2.2, '2023': 2.7, '2024': 3.1
    })

    print("Sample data loaded successfully!")

    # 5. Create Test User for Login
    if not User.objects.filter(username='testadmin').exists():
        User.objects.create_user('testadmin', 'test@example.com', 'password123')
        Usuario.objects.create(nombre="Test", ap="Admin", am="User", nombre_usuario="testadmin", email="test@example.com", contrasenia="password123", tipo="admin")
        print("Test user 'testadmin' created.")

if __name__ == '__main__':
    load_data()
