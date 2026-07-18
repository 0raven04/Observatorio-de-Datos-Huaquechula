import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()
from django.db import connection
cursor = connection.cursor()
cursor.execute("SHOW TABLES")
tables = [t[0] for t in cursor.fetchall()]
for t in sorted(tables):
    print(t)
print("---")
print("myapp_encuestacomercio" in tables)
print("myapp_encuestaresidente" in tables)
print("Encuesta" in tables)
