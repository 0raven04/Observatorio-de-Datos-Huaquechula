import django
import os
import subprocess

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.db import connection

cols_to_drop = [
    "beneficio_economico",
    "capacitacion_turistica",
    "interes_jovenes",
    "participacion_decisiones",
    "participacion_preservacion"
]

with connection.cursor() as cursor:
    for col in cols_to_drop:
        try:
            cursor.execute(f"ALTER TABLE myapp_encuestaresidente DROP COLUMN {col}")
            print(f"Successfully dropped: {col}")
        except Exception as e:
            print(f"Could not drop {col}: {e}")
            
    # Also drop tables if they were partially created in previous runs
    tables_to_drop = ["myapp_encuestainstitucional", "myapp_encuestavisitante"]
    for table in tables_to_drop:
        try:
            cursor.execute(f"DROP TABLE {table}")
            print(f"Successfully dropped table: {table}")
        except Exception as e:
            print(f"Could not drop table {table}: {e}")

print("Running migrate...")
result = subprocess.run(["python", "manage.py", "migrate"], capture_output=True, text=True)
print("STDOUT:")
print(result.stdout)
print("STDERR:")
print(result.stderr)
