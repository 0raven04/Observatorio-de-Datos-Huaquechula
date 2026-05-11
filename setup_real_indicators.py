import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from myapp.models import Indicador, Medicion, CategoriaIndicador

# Mapeo: { "Nombre Nuevo Exacto INEGI": ("ID INEGI", "Nombre Viejo en DB para buscar (opcional)") }
MAPPING = {
    'Esperanza de vida al nacer': ('6207019048', 'Esperanza de vida al nacer'),
    'Tasa de mortalidad infantil': ('6207019049', 'Tasa de mortalidad'),
    'Tasa de natalidad': ('6207019051', 'Salud auto reportada'),
    'Grado promedio de escolaridad': ('6207019050', 'Años promedio de escolaridad'),
    'Tasa de alfabetización': ('6207019053', 'Tasa de asistencia escolar'),
    'Población en pobreza': ('6200240364', 'Pobreza extrema'),
    'Población en pobreza extrema': ('6200240365', 'Desigualdad de ingresos'),
    'Población total': ('1002000001', 'Tasa de crecimiento poblacional') # Replacing some random one
}

print("Iniciando mapeo y limpieza de datos...")

for nuevo_nombre, (inegi_id, nombre_viejo) in MAPPING.items():
    # Buscar el indicador por nombre viejo o nuevo
    ind = Indicador.objects.filter(nombre__icontains=nombre_viejo).first()
    if not ind:
        ind = Indicador.objects.filter(nombre__icontains=nuevo_nombre).first()
        
    if ind:
        # Renombrar, asignar ID y fuente
        print(f"Actualizando: '{ind.nombre}' -> '{nuevo_nombre}'")
        ind.nombre = nuevo_nombre
        ind.inegi_indicator_id = inegi_id
        ind.data_source = 'inegi'
        ind.save()
        
        # Eliminar mediciones falsas
        mediciones_borradas = Medicion.objects.filter(indicador=ind).delete()
        print(f"  - Borradas {mediciones_borradas[0]} mediciones de prueba.")
    else:
        print(f"No se encontró indicador para reemplazar con '{nuevo_nombre}'")

print("Proceso completado.")
