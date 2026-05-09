# Usamos la versión de Python 3.11 slim, como se especificó
FROM python:3.11-slim

# Evitar la creación de archivos .pyc y forzar salida stdout (útil para logs)
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Definir directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema necesarias para mysqlclient y respaldos
RUN apt-get update && apt-get install -y \
    gcc \
    pkg-config \
    default-libmysqlclient-dev \
    default-mysql-client \
    && rm -rf /var/lib/apt/lists/*

# Crear usuario no root
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Copiar el archivo de dependencias e instalarlas
COPY requirements.txt /app/
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copiar el código del proyecto
COPY . /app/

# Asegurar que el usuario no-root tenga permisos en la carpeta principal
# y crear los volúmenes para static y media
RUN chown -R appuser:appuser /app && \
    chmod +x /app/entrypoint.sh && \
    mkdir -p /vol/web/media /vol/web/static && \
    chown -R appuser:appuser /vol && \
    chmod -R 755 /vol

# Cambiar al usuario no-root
USER appuser

# Exponer el puerto
EXPOSE 8000

# Punto de entrada
ENTRYPOINT ["/app/entrypoint.sh"]
