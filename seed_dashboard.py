import os
import django
import random
from datetime import timedelta
from django.utils import timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from myapp.models import Eje, CategoriaIndicador, Indicador, Medicion

# Limpiar datos existentes
Eje.objects.all().delete()
CategoriaIndicador.objects.all().delete()
Indicador.objects.all().delete()
Medicion.objects.all().delete()

# 1. EJES
eje_bienestar = Eje.objects.create(nombre="Bienestar Social", descripcion="Indicadores de bienestar, salud y educación")
eje_tradicion = Eje.objects.create(nombre="Tradición y Patrimonio", descripcion="Indicadores culturales y de patrimonio")
eje_turismo = Eje.objects.create(nombre="Turismo Comunitario", descripcion="Indicadores de actividad turística")

# 2. CATEGORÍAS (Total: 16)
# Bienestar (10)
cat_b_nombres = ["Salud", "Educación", "Pobreza y Desigualdad", "Vivienda", "Seguridad Pública", "Empleo y Economía Local", "Medio Ambiente", "Participación Ciudadana", "Servicios Públicos", "Demografía"]
cats_bienestar = [CategoriaIndicador.objects.create(eje=eje_bienestar, nombre=n) for n in cat_b_nombres]

# Tradición (3)
cat_t_nombres = ["Patrimonio Edificado", "Patrimonio Inmaterial", "Festividades y Eventos"]
cats_tradicion = [CategoriaIndicador.objects.create(eje=eje_tradicion, nombre=n) for n in cat_t_nombres]

# Turismo (3)
cat_tu_nombres = ["Afluencia Turística", "Derrama Económica", "Infraestructura Turística"]
cats_turismo = [CategoriaIndicador.objects.create(eje=eje_turismo, nombre=n) for n in cat_tu_nombres]

# 3. INDICADORES (Total: 47)
# Helper para crear mediciones mock
def create_mock_measurements(indicador, base_val, periods=5, variance=0.1):
    for i in range(periods):
        year = 2019 + i
        val = base_val * (1 + random.uniform(-variance, variance))
        if 'Tasa' in indicador.nombre or 'Porcentaje' in indicador.unidad_medida:
            val = round(val, 2)
        else:
            val = round(val)
        Medicion.objects.create(indicador=indicador, periodo=str(year), valor=val)

# BIENESTAR SOCIAL (32)
# Los que vimos en la imagen:
ind1 = Indicador.objects.create(categoria=cats_bienestar[0], nombre="Esperanza de vida", unidad_medida="Años", data_source="manual")
create_mock_measurements(ind1, 74.0, 5, 0.02)
Medicion.objects.create(indicador=ind1, periodo="2023", valor=75.50)

ind2 = Indicador.objects.create(categoria=cats_bienestar[0], nombre="Esperanza de vida al nacer", unidad_medida="Años", inegi_indicator_id="6207019048", data_source="inegi")
# Para que se vea en el dashboard aunque no haya sincronizado aún:
create_mock_measurements(ind2, 1.25, 5, 0.05)
Medicion.objects.create(indicador=ind2, periodo="2015", valor=1.29)

ind3 = Indicador.objects.create(categoria=cats_bienestar[0], nombre="Tasa de natalidad", unidad_medida="Porcentaje", inegi_indicator_id="1002000030", data_source="inegi")
create_mock_measurements(ind3, 0.25, 5, 0.05)
Medicion.objects.create(indicador=ind3, periodo="2015", valor=0.23)

ind4 = Indicador.objects.create(categoria=cats_bienestar[0], nombre="Tasa de mortalidad infantil", unidad_medida="Por cada 1000", inegi_indicator_id="6207019049", data_source="inegi")

# Completar hasta 32 para Bienestar
created_b = 4
for i in range(28):
    cat = cats_bienestar[i % len(cats_bienestar)]
    ind = Indicador.objects.create(categoria=cat, nombre=f"Indicador Bienestar {i+1}", unidad_medida="Unidades", data_source="manual")
    create_mock_measurements(ind, random.randint(50, 500))

# TRADICIÓN Y PATRIMONIO (8)
for i in range(8):
    cat = cats_tradicion[i % len(cats_tradicion)]
    ind = Indicador.objects.create(categoria=cat, nombre=f"Indicador Tradición {i+1}", unidad_medida="Eventos/Sitios", data_source="manual")
    create_mock_measurements(ind, random.randint(10, 100))

# TURISMO COMUNITARIO (7)
for i in range(7):
    cat = cats_turismo[i % len(cats_turismo)]
    ind = Indicador.objects.create(categoria=cat, nombre=f"Indicador Turismo {i+1}", unidad_medida="Visitantes/MXN", data_source="manual")
    create_mock_measurements(ind, random.randint(1000, 50000))

print("Se ha generado correctamente la estructura mock de indicadores.")
print(f"Ejes: {Eje.objects.count()}")
print(f"Categorías: {CategoriaIndicador.objects.count()}")
print(f"Indicadores: {Indicador.objects.count()}")
