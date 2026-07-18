import django
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.db import connection

columns_to_add = [
    ("tipo", "VARCHAR(20) NOT NULL DEFAULT 'reporte'"),
    ("url", "VARCHAR(500) NULL"),
    ("clasificacion", "VARCHAR(20) NOT NULL DEFAULT 'publico'"),
    ("clave_admin_id", "BIGINT NULL"),
]

with connection.cursor() as cursor:
    for col_name, col_def in columns_to_add:
        try:
            sql = f"ALTER TABLE myapp_documento ADD COLUMN {col_name} {col_def}"
            cursor.execute(sql)
            print(f"OK: Added column '{col_name}'")
        except Exception as e:
            print(f"SKIP: '{col_name}' -> {e}")

print("\nDone. Verifying columns:")
with connection.cursor() as cursor:
    cursor.execute("SHOW COLUMNS FROM myapp_documento")
    for row in cursor.fetchall():
        print(row)
