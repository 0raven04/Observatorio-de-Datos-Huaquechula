import django
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.db import connection

with connection.cursor() as cursor:
    # 1. Rename columns if they exist under old names
    try:
        cursor.execute("ALTER TABLE myapp_encuestaresidente CHANGE COLUMN alteracion_rutina tension_festividades SMALLINT UNSIGNED")
        print("Renamed alteracion_rutina to tension_festividades")
    except Exception as e:
        print(f"Skip rename alteracion_rutina: {e}")

    try:
        cursor.execute("ALTER TABLE myapp_encuestaresidente CHANGE COLUMN desvirtuacion_tradicion perdida_tradicion SMALLINT UNSIGNED")
        print("Renamed desvirtuacion_tradicion to perdida_tradicion")
    except Exception as e:
        print(f"Skip rename desvirtuacion_tradicion: {e}")

    # 2. Drop columns that will be added by migration 0020
    cols_to_drop = [
        "beneficio_economico",
        "capacitacion_turistica",
        "participacion_decisiones",
        "participacion_preservacion",
        "interes_jovenes"
    ]
    for col in cols_to_drop:
        try:
            cursor.execute(f"ALTER TABLE myapp_encuestaresidente DROP COLUMN {col}")
            print(f"Dropped column {col}")
        except Exception as e:
            print(f"Skip drop {col}: {e}")

    # 3. Add calidad_aire and gestion_residuos if they don't exist
    try:
        cursor.execute("ALTER TABLE myapp_encuestaresidente ADD COLUMN calidad_aire SMALLINT UNSIGNED NULL")
        print("Added calidad_aire")
    except Exception as e:
        print(f"Skip add calidad_aire: {e}")

    try:
        cursor.execute("ALTER TABLE myapp_encuestaresidente ADD COLUMN gestion_residuos SMALLINT UNSIGNED NULL")
        print("Added gestion_residuos")
    except Exception as e:
        print(f"Skip add gestion_residuos: {e}")

print("Alignment done.")
