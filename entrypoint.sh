#!/bin/bash
set -e

echo "Ejecutando migraciones de la base de datos..."
python manage.py migrate --noinput

echo "Recolectando archivos estáticos..."
python manage.py collectstatic --noinput

echo "Asegurando que la carpeta media y subcarpetas existen..."
mkdir -p /vol/web/media/kmz_files

# El comando a continuación arrancará el servidor web para desarrollo.
# Para producción se debería usar gunicorn o uWSGI.
echo "Iniciando servidor de desarrollo Django..."
exec python manage.py runserver 0.0.0.0:8000
