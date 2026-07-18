import django
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.db import connection

with connection.cursor() as cursor:
    # Add missing columns confianza_policia and percepcion_inseguridad
    try:
        cursor.execute("ALTER TABLE myapp_encuestaresidente ADD COLUMN confianza_policia SMALLINT UNSIGNED NULL")
        print("Added confianza_policia")
    except Exception as e:
        print(f"Skip add confianza_policia: {e}")

    try:
        cursor.execute("ALTER TABLE myapp_encuestaresidente ADD COLUMN percepcion_inseguridad SMALLINT UNSIGNED NULL")
        print("Added percepcion_inseguridad")
    except Exception as e:
        print(f"Skip add percepcion_inseguridad: {e}")

print("Alignment 2 done.")
