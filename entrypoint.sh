#!/bin/sh
set -e

echo "Ejecutando migraciones de la base de datos..."
python manage.py migrate --noinput

echo "Recolectando archivos estáticos..."
python manage.py collectstatic --noinput --clear

echo "Asegurando que la carpeta media y subcarpetas existen..."
mkdir -p /vol/web/media/kmz_files

echo "Iniciando servidor de desarrollo Django..."
if [ "$#" -eq 0 ]; then
    exec python manage.py runserver 0.0.0.0:8000
else
    exec "$@"
fi
