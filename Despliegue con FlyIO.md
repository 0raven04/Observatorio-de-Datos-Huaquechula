Aquí tienes el plan de despliegue y monitoreo para [Fly.io](https://fly.io/) y Better Stack. La diferencia principal con Railway es que [Fly.io](https://fly.io/) te da **máquinas virtuales (Machines)** que puedes iniciar, detener y destruir a voluntad, y que factura por segundo de uso activo[](https://flyio-landing.fly.dev/docs/about/cost-management/#metrics-based-autoscaling-can-affect-costs). Esto encaja muy bien con tu proyecto temporal: durante la temporada de recolección las máquinas corren, y al terminar las destruyes para dejar de pagar.

---

## 1. Arquitectura del despliegue en [Fly.io](https://fly.io/)

[Fly.io](https://fly.io/) no ejecuta `docker-compose.yml` directamente. Cada componente de tu stack se despliega como una **aplicación independiente** dentro de la misma organización, y se comunican por la **red privada interna** (`<app-name>.internal`)[](https://fly.io/docs/app-guides/mysql-on-fly/?source=post_page-----5f9f5cdb837b---------------------------------------).

Tu stack quedará así:

|Componente de tu repo|Aplicación en [Fly.io](https://fly.io/)|Cómo se despliega|
|---|---|---|
|**Backend Django** (API + Dashboard)|`observatorio-backend`|Desde tu repositorio con `fly launch` y el `Dockerfile` existente|
|**Base de datos MySQL**|`observatorio-mysql`|Contenedor oficial de MySQL con un **Fly Volume** persistente|

**Por qué MySQL como contenedor y no como servicio gestionado:** [Fly.io](https://fly.io/) **no ofrece un servicio MySQL gestionado** de forma nativa; su base de datos gestionada es PostgreSQL (Fly Postgres). Para mantener tu stack actual (MySQL), la ruta es desplegar MySQL como una aplicación separada con un volumen persistente. Esto es más trabajo operativo que un servicio gestionado, pero es perfectamente viable para un proyecto temporal de 1–2 meses.

---

## 2. Paso a paso del despliegue

### Paso 1: Instalar `flyctl` y autenticarte

bash

# macOS
brew install flyctl
# Linux
curl -L https://fly.io/install.sh | sh
# Autenticación
fly auth signup   # o fly auth login

Necesitas agregar un método de pago para usar el plan Pay As You Go, aunque el consumo para tu stack será bajo.

### Paso 2: Desplegar MySQL con volumen persistente

Crea un directorio separado para la aplicación de MySQL y ejecuta:

bash

mkdir observatorio-mysql && cd observatorio-mysql
fly launch --no-deploy --image mysql:8.0.37

Cuando te pregunte, dale un nombre como `observatorio-mysql` y **selecciona 2 GB de RAM** (MySQL 8 lo requiere para funcionar bien)[](https://fly.io/docs/app-guides/mysql-on-fly/?source=post_page-----5f9f5cdb837b---------------------------------------).

**Crea el volumen persistente:**

bash

fly volumes create mysqldata --size 10 --region <tu-region>

Sin este volumen, **perderías todos los datos en cada despliegue**[](https://fly.io/docs/app-guides/mysql-on-fly/?source=post_page-----5f9f5cdb837b---------------------------------------).

**Configura los secretos:**

bash

fly secrets set MYSQL_PASSWORD=tu_password_seguro
fly secrets set MYSQL_ROOT_PASSWORD=tu_root_password

**Edita el `fly.toml` generado** para que quede así:

toml

app = 'observatorio-mysql'
primary_region = "sjc"  # ajusta a tu región
[build]
  image = 'mysql:8.0.37'
[[vm]]
  cpu_kind = 'shared'
  cpus = 1
  memory_mb = 2048
[processes]
  app = """--datadir /data/mysql \
  --default-authentication-plugin mysql_native_password"""
[mounts]
  source = "mysqldata"
  destination = "/data"
[env]
  MYSQL_DATABASE = "observatorio"
  MYSQL_USER = "observatorio_user"

**Nota importante:** Elimina cualquier bloque `[[http_service]]` que `fly launch` haya generado, porque MySQL no expone HTTP[](https://fly.io/docs/app-guides/mysql-on-fly/?source=post_page-----5f9f5cdb837b---------------------------------------).

**Despliega:**

bash

fly deploy

### Paso 3: Desplegar el backend Django

Desde el directorio de tu repositorio principal:

bash

fly launch --no-deploy

Responde:

- **App name:** `observatorio-backend` (o el que prefieras)
    
- **Region:** la misma que usaste para MySQL
    
- **Use Postgres:** No (ya tienes MySQL)
    
- **Create Dockerfile:** No (ya tienes uno)
    

**Configura los secretos** ([Fly.io](https://fly.io/) los cifra en reposo y los inyecta como variables de entorno en el arranque de la VM):

bash

fly secrets set SECRET_KEY=$(python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())")
fly secrets set ALLOWED_HOSTS="observatorio-backend.fly.dev,tu-dominio.com"
fly secrets set DB_HOST="observatorio-mysql.internal"
fly secrets set DB_PORT="3306"
fly secrets set DB_NAME="observatorio"
fly secrets set DB_USER="observatorio_user"
fly secrets set DB_PASSWORD="tu_password_seguro"

**Configura el `fly.toml` del backend** con health check y los ajustes necesarios:

toml

app = 'observatorio-backend'
primary_region = "sjc"
[build]
  dockerfile = "Dockerfile"
[[vm]]
  cpu_kind = 'shared'
  cpus = 1
  memory_mb = 512
[http_service]
  internal_port = 8000
  force_https = true
  auto_stop_machines = 'suspend'
  auto_start_machines = true
  min_machines_running = 0
  [[http_service.checks]]
    interval = "30s"
    timeout = "5s"
    grace_period = "30s"
    method = "GET"
    path = "/api/health/encuestas/"

El health check hace que [Fly.io](https://fly.io/) no enrute tráfico a una máquina hasta que el endpoint responda con un 2xx[](https://flyio-landing.fly.dev/docs/blueprints/seamless-deployments/#main-content-start). El `auto_stop_machines = 'suspend'` hace que la máquina se duerma cuando no hay tráfico y despierte automáticamente al recibir una petición, lo que reduce drásticamente el costo durante períodos de baja actividad[](https://flyio-landing.fly.dev/docs/about/cost-management/#metrics-based-autoscaling-can-affect-costs).

**Despliega:**

bash

fly deploy

### Paso 4: Ejecutar migraciones y crear superusuario

Usa la consola SSH de [Fly.io](https://fly.io/) para conectarte a la máquina:

bash

fly ssh console -a observatorio-backend
# Dentro de la consola:
python manage.py migrate
python manage.py createsuperuser
exit

### Paso 5: Configurar el dominio personalizado

bash

fly certs add tu-dominio.com
fly certs show tu-dominio.com

[Fly.io](https://fly.io/) te mostrará los registros DNS que debes configurar en tu registrador (Namecheap, Porkbun, etc.):

- Un registro **A** o **AAAA** que apunte a la IP de tu aplicación.
    
- Un registro **TXT** de verificación de propiedad (`_fly-ownership`).
    

Una vez que los registros propaguen, [Fly.io](https://fly.io/) emitirá automáticamente un **certificado SSL de Let's Encrypt** y lo renovará cada 90 días sin intervención tuya.

Si usas Cloudflare para gestionar tu DNS, ponlo en modo **"DNS only"** (nube gris) durante la verificación, y luego puedes activar el proxy si lo deseas.

---

## 3. Monitoreo con Better Stack

El objetivo es verificar que las encuestas móviles lleguen a la API y se reflejen en el dashboard. Usaremos **dos monitores complementarios**.

### Monitor 1: Uptime (disponibilidad del servicio)

Este monitor verifica que tu backend esté vivo y respondiendo correctamente.

**Endpoint de health check en Django:**

python

from django.http import JsonResponse
from django.utils import timezone
from .models import Encuesta  # Ajusta al nombre de tu modelo
def health_encuestas(request):
    ultima = Encuesta.objects.order_by('-fecha_creacion').first()
    total_hoy = Encuesta.objects.filter(fecha_creacion__date=timezone.now().date()).count()
    return JsonResponse({
        "status": "ok",
        "ultima_encuesta": ultima.fecha_creacion.isoformat() if ultima else None,
        "total_hoy": total_hoy
    })

**Configuración en Better Stack:**

- **Tipo de monitor:** HTTP con verificación de palabra clave.
    
- **URL:** `https://tu-dominio.com/api/health/encuestas/`
    
- **Expected Status Code:** `200`
    
- **Required Keyword:** `"status": "ok"`
    
- **Frecuencia de chequeo:** cada 3 minutos (plan gratuito) o cada 30 segundos (planes pagos).
    

Better Stack usa este endpoint para verificar que el servicio responde, pero **no detecta si los datos están fluyendo**. Para eso está el siguiente monitor.

### Monitor 2: Heartbeat (latido del flujo de datos)

Este es el monitor **crítico para tu caso**. Detecta si la app móvil dejó de enviar encuestas, incluso si el servidor sigue "vivo".

**Implementación en Django:**

En la vista que recibe el POST de la app móvil, después de guardar la encuesta, envía una señal a Better Stack:

python

import requests
def crear_encuesta(request):
    # ... tu lógica para guardar la encuesta ...
    encuesta.save()
    
    # Notificar a Better Stack
    try:
        requests.get(
            "https://uptime.betterstack.com/api/v1/heartbeat/TU_TOKEN_UNICO",
            timeout=5
        )
    except requests.exceptions.RequestException:
        pass  # No bloquear la respuesta al usuario si falla la notificación
    
    return JsonResponse({"status": "created"}, status=201)

**Configuración del Heartbeat en Better Stack:**

1. Ve a **Heartbeats → Create heartbeat**.
    
2. Nómbralo, por ejemplo, "Flujo de encuestas móviles".
    
3. Copia la URL única que te genera.
    
4. **Expect a heartbeat every:** `60 minutes` (ajústalo según la frecuencia esperada de encuestas).
    
5. **Grace period:** `10 minutes` (tiempo de margen antes de disparar la alerta).
    

Si el flujo se detiene por un problema en la app móvil, la red o el backend, Better Stack te avisará automáticamente.

### Configuración de alertas

Better Stack permite alertas por **email, Slack, SMS, llamadas telefónicas, Microsoft Teams y webhooks**. Para un proyecto temporal, configura:

- **Email:** para todo el equipo.
    
- **Slack:** si el equipo lo usa, con menciones al responsable.
    
- **SMS:** como respaldo para alertas críticas (caída del servicio o flujo detenido).
    

Configura **políticas de escalado**: si la primera persona no responde en 15 minutos, se notifica a la segunda.

---

## 4. Dashboard de verificación visual

Además de las alertas automáticas, añade un widget simple en tu dashboard web para verificar el flujo de un vistazo:

html

<div class="status-widget">
    <h3>Estado del Flujo de Encuestas</h3>
    <p>Última encuesta recibida: <strong>{{ ultima_encuesta|timesince }}</strong></p>
    <p>Total de encuestas hoy: <strong>{{ total_hoy }}</strong></p>
    <p>Total general: <strong>{{ total_general }}</strong></p>
</div>

Si "Última encuesta recibida" muestra "hace 2 horas" cuando debería mostrar "hace 5 minutos", hay un problema que debes investigar antes de que Better Stack dispare la alerta.

---

## 5. Costos y ciclo de vida para tu proyecto temporal

### Estimación de costos en [Fly.io](https://fly.io/)

|Recurso|Configuración|Costo mensual (24/7)|
|---|---|---|
|**Backend Django**|`shared-cpu-1x`, 512 MB RAM|~$3.19/mes[](https://github.com/Oppkey/fastopp/blob/main/docs/deployment/FLY_DEPLOYMENT.md#1)|
|**MySQL**|`shared-cpu-1x`, 2 GB RAM|~$12–15/mes|
|**Volumen MySQL**|10 GB|~$1.50/mes ($0.15/GB-mes)[](https://github.com/Oppkey/fastopp/blob/main/docs/deployment/FLY_DEPLOYMENT.md#1)|
|**Transferencia de datos**|160 GB gratis|$0 (dentro del free tier)|
|**Total estimado**||**~$16–20/mes**|

**Con auto-stop activado** en el backend, la máquina de Django se suspende cuando no hay tráfico y solo pagas por el tiempo activo. Para un flujo de encuestas intermitente, el costo real podría ser **$10–15/mes**.

### Ciclo de vida: activar y destruir

**Al iniciar la temporada:**

bash

fly deploy -a observatorio-backend
fly deploy -a observatorio-mysql

**Al terminar la temporada (destruir todo):**

bash

fly apps destroy observatorio-backend
fly apps destroy observatorio-mysql

**Importante:** Al destruir una app, **se eliminan sus volúmenes y todas las instantáneas**. Antes de destruir, exporta los datos de la base de datos con `mysqldump` y guárdalos en tu equipo o en un almacenamiento externo[](https://fly.io/docs/apps/delete/). [Fly.io](https://fly.io/) toma **instantáneas automáticas diarias** de los volúmenes (con retención de 5 días por defecto), pero al destruir la app también se destruyen esas instantáneas.

### Dominio fuera de temporada

Mantén el dominio registrado durante todo el año. Durante la temporada, los registros DNS apuntan a [Fly.io](https://fly.io/). Fuera de temporada, activa el **parking** del registrador o una redirección temporal a tu repositorio de GitHub.

---

## 6. Checklist de verificación antes de producción

- □
    
    El backend responde correctamente en `https://tu-dominio.com/api/health/encuestas/`.
    
- □
    
    El health check de [Fly.io](https://fly.io/) muestra la máquina como `passing` (`fly checks list`).
    
- □
    
    El monitor de uptime en Better Stack muestra estado verde.
    
- □
    
    El heartbeat recibe señales cada vez que se crea una encuesta desde la app móvil.
    
- □
    
    Has simulado una caída del backend (`fly apps suspend` o deteniendo la máquina) y verificado que Better Stack dispara la alerta.
    
- □
    
    Has simulado un cese del flujo de encuestas (dejando de enviar heartbeats) y verificado que la alerta de heartbeat se dispara.
    
- □
    
    El dominio personalizado resuelve correctamente y el SSL está activo.
    
- □
    
    La app móvil apunta al endpoint de producción de [Fly.io](https://fly.io/).
    
- □
    
    Los conteos en el dashboard coinciden con los datos en la base de datos.
    
- □
    
    Has exportado un `mysqldump` de respaldo antes de cualquier operación destructiva.
    

---

## 7. Comparativa rápida: [Fly.io](https://fly.io/) vs Railway para tu caso

|Criterio|Railway|[Fly.io](https://fly.io/)|
|---|---|---|
|**MySQL**|Gestionado con un clic|Contenedor manual con volumen|
|**Facilidad de despliegue**|Muy alta (detecta Dockerfile)|Alta (requiere `fly launch` y ajustar `fly.toml`)|
|**Costo estimado 1–2 meses**|~$10–15/mes|~$16–20/mes (o ~$10–15 con auto-stop)|
|**Control sobre recursos**|Limitado (planes predefinidos)|Total (eliges CPU, RAM, región)|
|**Destrucción de recursos**|Eliminar proyecto|`fly apps destroy` por app|
|**Monitoreo integrado**|Básico (logs y métricas)|Health checks nativos en `fly.toml`|

**Recomendación:** Si valoras la simplicidad y ya tienes el `docker-compose.yml` funcionando, **Railway es más directo**. Si quieres control granular sobre las máquinas y prefieres no depender de un servicio gestionado para la base de datos, **[Fly.io](https://fly.io/) es más flexible**. Ambos se integran perfectamente con Better Stack.

Si quieres, puedo detallarte el `Dockerfile` para el contenedor de MySQL o la configuración exacta del monitor de keyword en Better Stack.