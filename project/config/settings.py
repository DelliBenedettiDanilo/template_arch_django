"""
Django settings for exolab project.
"""
import os
from pathlib import Path
import environ

BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env(
    DEBUG=(bool, False),
)

# Cerca il file .env.dev o .env.prod se si lancia Django fuori da Docker
ENV_FILE = BASE_DIR.parent / ".env"
if not ENV_FILE.exists():
    # Fallback se il file è nominato esplicitamente in locale
    ENV_FILE = BASE_DIR.parent / ".env.dev"

if ENV_FILE.exists():
    environ.Env.read_env(ENV_FILE)

SECRET_KEY = env("SECRET_KEY")
DEBUG = env.bool("DEBUG", default=False)

# "localhost"/"127.0.0.1" sono sempre ammessi: servono all'healthcheck interno
# del container Docker (curl/urllib verso localhost:8000), non al traffico reale
# che passa da nginx con l'Host header del dominio configurato sopra.
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=[]) + ["localhost", "127.0.0.1"]
CSRF_TRUSTED_ORIGINS = env.list("CSRF_TRUSTED_ORIGINS", default=[])
CORS_ALLOWED_ORIGINS = env.list("CORS_ALLOWED_ORIGINS", default=[])

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    
    # Terze parti richieste per architettura modulare
    "corsheaders",
    
    # App locali
    "core.apps.CoreConfig",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",  # Fondamentale per la gestione statici in produzione
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",       # Deve stare sopra CommonMiddleware
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

# Autenticazione: home è protetta da @login_required (vedi core/views.py),
# quindi Django deve sapere dove mandare gli utenti non autenticati e dove
# riportarli dopo un login riuscito.
LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "home"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],  # Predisposta cartella globale templates
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

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

# Database Config via URL
DATABASES = {
    "default": env.db("DATABASE_URL")
}

# Configurazione del Caching con backend nativo Django (usa la libreria 'redis' standard)
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": env("REDIS_URL", default="redis://redis:6379/1"),
        "KEY_PREFIX": "{{ cookiecutter.project_slug }}_cache",
        "TIMEOUT": 300,
    }
}

# Gestione Sessioni su Redis
SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "default"

# Sicurezza Sessioni e Cookie (Ottimo setup basato sulle tue variabili)
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
SESSION_COOKIE_SECURE = env.bool("DJANGO_SESSION_COOKIE_SECURE", default=not DEBUG)

CSRF_COOKIE_HTTPONLY = False  # Lasciato a False se devi leggere il token via JS/Frontend
CSRF_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_SECURE = env.bool("DJANGO_CSRF_COOKIE_SECURE", default=not DEBUG)

# Header di Sicurezza avanzati
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"
SECURE_SSL_REDIRECT = env.bool("DJANGO_SECURE_SSL_REDIRECT", default=not DEBUG)
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
USE_X_FORWARDED_HOST = True

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# Internazionalizzazione
LANGUAGE_CODE = "it-it"
TIME_ZONE = "Europe/Rome"
USE_I18N = True
USE_TZ = True

# Gestione Asset Statici e Media allineati ai Volumi Docker ed Exolab
STATIC_URL = env("DJANGO_STATIC_URL", default="/static/")
STATIC_ROOT = "/app/staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]

# Ottimizzazione WhiteNoise in produzione (compressione asset)
if not DEBUG:
    STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

MEDIA_URL = env("DJANGO_MEDIA_URL", default="/media/")
MEDIA_ROOT = "/app/mediafiles"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Configurazione Dinamica dei Log (Usa la variabile DJANGO_LOG_LEVEL)
LOG_LEVEL = env("DJANGO_LOG_LEVEL", default="INFO")
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {process:d} {thread:d} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": LOG_LEVEL,
    },
}