#!/bin/sh
set -e

echo "==> Ejecutando migraciones de la base de datos..."
python manage.py migrate --noinput

echo "==> Recolectando archivos estáticos..."
python manage.py collectstatic --noinput --clear

echo "==> Creando carpetas de media necesarias..."
mkdir -p /vol/web/media/kmz_files

echo "==> Iniciando Gunicorn (servidor de producción)..."
exec gunicorn mysite.wsgi:application \
    --bind 0.0.0.0:${PORT:-8000} \
    --workers ${GUNICORN_WORKERS:-3} \
    --timeout ${GUNICORN_TIMEOUT:-120} \
    --log-level ${GUNICORN_LOG_LEVEL:-info} \
    --access-logfile - \
    --error-logfile -
