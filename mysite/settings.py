import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()  # Carga las variables de entorno del .env

BASE_DIR = Path(__file__).resolve().parent.parent

# Seguridad
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "unsafe-default-key")
DEBUG = os.getenv("DJANGO_DEBUG", "False") == "True"
ALLOWED_HOSTS = os.getenv("DJANGO_ALLOWED_HOSTS", "*").split(",")

# URLs de login/logout
LOGIN_URL = os.getenv("DJANGO_LOGIN_URL", "/login/")
LOGIN_REDIRECT_URL = os.getenv("DJANGO_LOGIN_REDIRECT_URL", "/redirigir/")
LOGOUT_REDIRECT_URL = os.getenv("DJANGO_LOGOUT_REDIRECT_URL", "/login/")

# Aplicaciones
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "myapp",
    "django.contrib.staticfiles",
]

# Middleware
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    'whitenoise.middleware.WhiteNoiseMiddleware',
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "mysite.urls"

# Templates
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "myapp/templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "mysite.wsgi.application"

# Base de datos
DATABASES = {
    "default": {
        "ENGINE": os.getenv("DB_ENGINE", "django.db.backends.sqlite3"),
        "NAME": os.getenv("DB_NAME", BASE_DIR / "db.sqlite3"),
        "USER": os.getenv("DB_USER", ""),
        "PASSWORD": os.getenv("DB_PASSWORD", ""),
        "HOST": os.getenv("DB_HOST", "localhost"),
        "PORT": os.getenv("DB_PORT", ""),
        "OPTIONS": (
            {
                "init_command": "SET sql_mode='STRICT_TRANS_TABLES', innodb_strict_mode=1",
                "charset": "utf8mb4",
                "isolation_level": "read committed",
            }
            if "mysql" in os.getenv("DB_ENGINE", "")
            else {}
        ),
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# Internacionalización
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# Archivos estáticos y media
STATIC_URL = os.getenv("STATIC_URL", "/static/")
STATICFILES_DIRS = [os.path.join(BASE_DIR, "myapp/static")]
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

MEDIA_URL = os.getenv("MEDIA_URL", "/media/")
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

# Autenticación personalizada
AUTHENTICATION_BACKENDS = [
    "myapp.authentication_backend.UsuarioBackend",
    "django.contrib.auth.backends.ModelBackend",
]

# Archivos permitidos
ALLOWED_EXTENSIONS = set(os.getenv("ALLOWED_EXTENSIONS", "").split(","))
MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", 10_000_000))

# Default primary key
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
