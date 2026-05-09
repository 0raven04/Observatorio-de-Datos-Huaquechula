# Observatorio de Datos Huaquechula

Este repositorio contiene la aplicación del Observatorio Turístico de Huaquechula. El proyecto está contenerizado usando **Docker** y **Docker Compose** para facilitar su desarrollo, distribución e implementación.

## Requisitos Previos

Asegúrate de tener instalados los siguientes programas en tu sistema:
- [Git](https://git-scm.com/downloads)
- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)

## Configuración y Ejecución del Contenedor

Sigue estos pasos para construir y levantar el proyecto por primera vez:

### 1. Clonar el repositorio
Abre tu terminal y clona el proyecto en tu máquina local:
```bash
git clone <URL_DEL_REPOSITORIO>
cd Observatorio-de-Datos-Huaquechula
```

### 2. Configurar las variables de entorno
El proyecto requiere de un archivo oculto llamado `.env` para manejar las contraseñas y configuraciones sensibles.
Copia el archivo de ejemplo proporcionado para crear tu propia configuración:
```bash
cp .env.example .env
```
*(Opcional)*: Puedes abrir el archivo `.env` en tu editor de texto y cambiar las contraseñas o claves si lo deseas. Para entornos de desarrollo local, los valores por defecto suelen ser suficientes.

### 3. Construir e iniciar los contenedores
Ejecuta el siguiente comando para descargar las imágenes base, instalar dependencias y levantar tanto la base de datos (MySQL) como la aplicación web (Django):
```bash
docker-compose up --build -d
```
> **Nota:** El parámetro `-d` (detached) permite que los contenedores se ejecuten en segundo plano para que puedas seguir usando tu terminal.

### 4. Creación del Superusuario (Admin)
El contenedor está configurado con un script (`entrypoint.sh`) que aplica automáticamente las migraciones de la base de datos y recolecta archivos estáticos cada vez que arranca.
Sin embargo, para acceder al panel de administración necesitas crear un usuario administrador:
```bash
docker-compose exec web python manage.py createsuperuser
```
*(Sigue las instrucciones en pantalla para ingresar un nombre de usuario, correo y contraseña).*

## ¿Cómo ingresar a la página?

- **Página principal de la aplicación:**
  Abre tu navegador web y visita: [http://localhost:8000](http://localhost:8000)
- **Base de Datos MySQL:**
  El gestor de base de datos MySQL expone el puerto `3306`. Puedes conectarte usando cualquier cliente SQL (como DBeaver, Workbench o DataGrip) apuntando a `localhost:3306` con el usuario `root` y la contraseña definida en tu archivo `.env`.

## Comandos Útiles de Docker

- **Ver el registro (logs) de la página web en tiempo real:**
  ```bash
  docker-compose logs -f web
  ```
- **Ver el registro de la base de datos:**
  ```bash
  docker-compose logs -f db
  ```
- **Detener todos los servicios:**
  ```bash
  docker-compose down
  ```
- **Reiniciar la aplicación (útil si instalaste algo nuevo o necesitas reiniciar):**
  ```bash
  docker-compose restart web
  ```
- **Entrar a la consola bash dentro del contenedor de Django:**
  ```bash
  docker-compose exec web bash
  ```

## Posibles Errores y Soluciones

#### ❌ Error: `Can't connect to MySQL server on 'db' (111)`
**Por qué pasa:** La aplicación de Django intentó conectarse a MySQL antes de que la base de datos estuviera 100% inicializada (la base de datos tarda más en arrancar la primera vez).
**Solución:** En `docker-compose.yml` hay un `healthcheck` para evitarlo, pero si el problema persiste, solo dale un par de segundos y reinicia el servicio web:
```bash
docker-compose restart web
```

#### ❌ Error: `ModuleNotFoundError: No module named '...'`
**Por qué pasa:** Se agregó una nueva librería al archivo `requirements.txt` pero no has reconstruido la imagen de Docker para que la instale.
**Solución:** Reconstruye la imagen ejecutando:
```bash
docker-compose up --build -d
```

#### ❌ Error: `Ports are not available: listen tcp 0.0.0.0:8000: bind: address already in use`
**Por qué pasa:** Ya tienes otro programa o servicio ocupando el puerto 8000 o 3306 en tu computadora.
**Solución:** Detén el servicio que esté ocupando el puerto, o bien, entra al archivo `docker-compose.yml` y cambia el puerto izquierdo. Ejemplo: de `"8000:8000"` a `"8080:8000"`. Luego accede a `http://localhost:8080`.

#### ❌ Error: Los cambios en HTML/CSS/Python no se reflejan en la página.
**Por qué pasa:** A veces el caché del navegador engaña, o Python compiló archivos internamente.
**Solución:**
1. Recarga la página vaciando caché usando `Ctrl + F5`.
2. Si hiciste cambios pesados en el backend, reinicia el contenedor: `docker-compose restart web`.
3. Si subiste el proyecto a producción, tal vez necesitas recolectar estáticos: `docker-compose exec web python manage.py collectstatic --noinput`.
