import django
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.db import connection

with connection.cursor() as cursor:
    cursor.execute("SHOW COLUMNS FROM myapp_encuestaresidente")
    for row in cursor.fetchall():
        print(row)
