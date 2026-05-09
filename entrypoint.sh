#!/bin/bash
set -e

echo "Ejecutando migraciones de la base de datos..."
python manage.py migrate --noinput

echo "Recolectando archivos estáticos..."
python manage.py collectstatic --noinput

echo "Asegurando que la carpeta media y subcarpetas existen..."
mkdir -p /vol/web/media/kmz_files

echo "Iniciando Gunicorn..."
exec gunicorn mysite.wsgi:application --bind 0.0.0.0:8000 --workers ${GUNICORN_WORKERS:-3} --timeout ${GUNICORN_TIMEOUT:-60}
