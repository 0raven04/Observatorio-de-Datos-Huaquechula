# =============================================
# ETAPA 1: Build — instalación de dependencias
# =============================================
FROM python:3.11-slim AS builder

# Evitar archivos .pyc y forzar logs en stdout
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Dependencias del sistema necesarias para compilar mysqlclient
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    pkg-config \
    default-libmysqlclient-dev \
    && rm -rf /var/lib/apt/lists/*

# Copiar e instalar dependencias Python en una carpeta aislada
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt


# =============================================
# ETAPA 2: Runtime — imagen final ligera
# =============================================
FROM python:3.11-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000

WORKDIR /app

# Instalar solo las librerías de sistema en tiempo de ejecución (no el compilador)
RUN apt-get update && apt-get install -y --no-install-recommends \
    default-libmysqlclient-dev \
    default-mysql-client \
    && rm -rf /var/lib/apt/lists/*

# Copiar los paquetes Python instalados desde el builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Crear usuario no-root para mayor seguridad
RUN groupadd -r appuser && useradd -m -r -g appuser appuser

# Copiar el código del proyecto
COPY . /app/

# Crear carpetas de volúmenes y asignar permisos
RUN mkdir -p /vol/web/media/kmz_files /vol/web/static /home/appuser && \
    chown -R appuser:appuser /app /vol /home/appuser && \
    chmod -R 755 /vol && \
    chmod +x /app/entrypoint.prod.sh

# Cambiar al usuario no-root
USER appuser

# Exponer el puerto de Gunicorn
EXPOSE 8000

# Punto de entrada de producción (usa Gunicorn)
ENTRYPOINT ["/app/entrypoint.prod.sh"]
