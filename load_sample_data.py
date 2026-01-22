
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

    # 4. Create Measurements
    # Salud
    Medicion.objects.get_or_create(indicador=ind_esp_vida, periodo="2023", defaults={'valor': 75.5})
    Medicion.objects.get_or_create(indicador=ind_salud_auto, periodo="2023", defaults={'valor': 68.2})
    Medicion.objects.get_or_create(indicador=ind_obesidad, periodo="2023", defaults={'valor': 33.4})
    Medicion.objects.get_or_create(indicador=ind_mortalidad, periodo="2023", defaults={'valor': 5.8})
    Medicion.objects.get_or_create(indicador=ind_mort_materna, periodo="2023", defaults={'valor': 34.5})
    
    # Accesibilidad a servicios
    Medicion.objects.get_or_create(indicador=ind_acceso_salud, periodo="2023", defaults={'valor': 82.3})
    Medicion.objects.get_or_create(indicador=ind_banda_ancha, periodo="2023", defaults={'valor': 56.7})
    Medicion.objects.get_or_create(indicador=ind_servicios_basicos, periodo="2023", defaults={'valor': 91.2})
    
    # Educación
    Medicion.objects.get_or_create(indicador=ind_niveles_educacion, periodo="2023", defaults={'valor': 45.8})
    Medicion.objects.get_or_create(indicador=ind_desercion_escolar, periodo="2023", defaults={'valor': 8.3})
    Medicion.objects.get_or_create(indicador=ind_anios_escolaridad, periodo="2023", defaults={'valor': 9.2})
    
    # Vivienda
    Medicion.objects.get_or_create(indicador=ind_habitaciones_persona, periodo="2023", defaults={'valor': 1.2})
    Medicion.objects.get_or_create(indicador=ind_techos_resistentes, periodo="2023", defaults={'valor': 87.5})
    
    # Ingresos
    Medicion.objects.get_or_create(indicador=ind_gini, periodo="2023", defaults={'valor': 0.42})
    Medicion.objects.get_or_create(indicador=ind_ingreso_equiv, periodo="2023", defaults={'valor': 8750.50})
    Medicion.objects.get_or_create(indicador=ind_pobreza_ingresos, periodo="2023", defaults={'valor': 12500})
    Medicion.objects.get_or_create(indicador=ind_pobreza_extrema, periodo="2023", defaults={'valor': 3200})
    
    # Empleo
    Medicion.objects.get_or_create(indicador=ind_condiciones_criticas, periodo="2023", defaults={'valor': 12.8})
    Medicion.objects.get_or_create(indicador=ind_informalidad, periodo="2023", defaults={'valor': 56.3})
    Medicion.objects.get_or_create(indicador=ind_desocupacion, periodo="2023", defaults={'valor': 3.5})
    Medicion.objects.get_or_create(indicador=ind_participacion_econ, periodo="2023", defaults={'valor': 58.7})
    
    # Seguridad
    Medicion.objects.get_or_create(indicador=ind_homicidios, periodo="2023", defaults={'valor': 15.2})
    Medicion.objects.get_or_create(indicador=ind_confianza_policia, periodo="2023", defaults={'valor': 42.5})
    Medicion.objects.get_or_create(indicador=ind_percepcion_inseguridad, periodo="2023", defaults={'valor': 68.9})
    Medicion.objects.get_or_create(indicador=ind_incidencia_delictiva, periodo="2023", defaults={'valor': 320.5})
    
    # Medio ambiente
    Medicion.objects.get_or_create(indicador=ind_contaminacion_aire, periodo="2023", defaults={'valor': 28.3})
    Medicion.objects.get_or_create(indicador=ind_disposicion_residuos, periodo="2023", defaults={'valor': 78.5})
    Medicion.objects.get_or_create(indicador=ind_gestion_ambiental, periodo="2023", defaults={'valor': 5})
    
    # Migración
    Medicion.objects.get_or_create(indicador=ind_intensidad_migratoria, periodo="2023", defaults={'valor': 1.8})
    
    # Tradición y Patrimonio - PCI
    Medicion.objects.get_or_create(indicador=ind_tension_poblacion, periodo="2023", defaults={'valor': 2.3})
    Medicion.objects.get_or_create(indicador=ind_acceso_servicios_tradicion, periodo="2023", defaults={'valor': 65.4})
    Medicion.objects.get_or_create(indicador=ind_tensiones_fisicas, periodo="2023", defaults={'valor': 1.8})
    
    # Tradición y Patrimonio - Salvaguardia
    Medicion.objects.get_or_create(indicador=ind_procesos_salvaguardia, periodo="2023", defaults={'valor': 3})
    Medicion.objects.get_or_create(indicador=ind_seguimiento_salvaguardia, periodo="2023", defaults={'valor': 2.5})
    Medicion.objects.get_or_create(indicador=ind_difusion_pci, periodo="2023", defaults={'valor': 8})
    Medicion.objects.get_or_create(indicador=ind_relacion_comunidad_pci, periodo="2023", defaults={'valor': 3.2})
    
    # Turismo Comunitario - Participación y gobernanza
    Medicion.objects.get_or_create(indicador=ind_participacion_decisiones, periodo="2023", defaults={'valor': 45.3})
    Medicion.objects.get_or_create(indicador=ind_capacitacion_info, periodo="2023", defaults={'valor': 2.8})
    Medicion.objects.get_or_create(indicador=ind_regulacion, periodo="2023", defaults={'valor': 2.1})
    
    # Turismo Comunitario - Gestión del turismo
    Medicion.objects.get_or_create(indicador=ind_herramientas_gestion, periodo="2023", defaults={'valor': 4})
    Medicion.objects.get_or_create(indicador=ind_proyectos_turisticos, periodo="2023", defaults={'valor': 6})
    Medicion.objects.get_or_create(indicador=ind_integracion_territorial, periodo="2023", defaults={'valor': 2.7})

    print("Sample data loaded successfully!")

    # 5. Create Test User for Login
    if not User.objects.filter(username='testadmin').exists():
        User.objects.create_user('testadmin', 'test@example.com', 'password123')
        Usuario.objects.create(nombre="Test", ap="Admin", am="User", nombre_usuario="testadmin", email="test@example.com", contrasenia="password123", tipo="admin")
        print("Test user 'testadmin' created.")

if __name__ == '__main__':
    load_data()
