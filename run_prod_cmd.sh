#!/bin/bash
# ==============================================================================
# Script para ejecutar comandos de Django directamente en la BD de Producción
# ==============================================================================
# Este script utiliza tu imagen de Docker local pero se conecta a la base de 
# datos MySQL en Azure. Esto es ideal para:
# - Crear superusuarios (createsuperuser)
# - Cargar datos (loaddata)
# - Ejecutar migraciones (migrate)
#
# Uso:
#   ./run_prod_cmd.sh <comando_django>
# Ejemplo:
#   ./run_prod_cmd.sh createsuperuser
# ==============================================================================

# 1. Obtener tu IP pública para abrir el firewall temporalmente
echo "🔍 Obteniendo IP pública..."
MY_IP=$(curl -s https://api.ipify.org)
echo "Tu IP pública es: $MY_IP"

# 2. Abrir el firewall en Azure MySQL
echo "🔓 Abriendo firewall temporal en Azure MySQL para tu IP..."
az mysql flexible-server firewall-rule create \
  --resource-group rg-observatorio-prod \
  --name db-observatorio-huaquechula \
  --rule-name "allow-local-command" \
  --start-ip-address "$MY_IP" \
  --end-ip-address "$MY_IP" > /dev/null

echo "✅ Firewall abierto."
echo "🚀 Ejecutando: python manage.py $@"
echo "------------------------------------------------------"

# 3. Ejecutar el comando usando Docker apuntando a Producción
# Usamos -it para permitir interactividad (ej. createsuperuser)
docker run -it --rm \
  -e DB_HOST="db-observatorio-huaquechula.mysql.database.azure.com" \
  -e DB_NAME="observatorio_db" \
  -e DB_USER="django_admin" \
  -e DB_PASSWORD="J22240007j" \
  -e DB_PORT="3306" \
  -e DEBUG="False" \
  -e SECRET_KEY="django-insecure-)xzi6t)9" \
  -e ALLOWED_HOSTS="localhost" \
  -e AZURE_STORAGE_ACCOUNT_NAME="" \
  -e ML_MODEL_PATH="disabled" \
  --entrypoint python \
  kevinarana/observatorio-de-datos-huaquechula-web:latest \
  manage.py "$@"

echo "------------------------------------------------------"

# 4. Cerrar el firewall por seguridad
echo "🔒 Cerrando regla de firewall temporal..."
az mysql flexible-server firewall-rule delete \
  --resource-group rg-observatorio-prod \
  --name db-observatorio-huaquechula \
  --rule-name "allow-local-command" \
  --yes > /dev/null

echo "✅ Listo. Firewall cerrado y base de datos segura."
