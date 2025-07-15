import os
from pathlib import Path
from dotenv import load_dotenv
import dj_database_url

# Load .env if present
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# Key and debug
SECRET_KEY = os.getenv('SECRET_KEY', 'your-unsafe-local-dev-key')
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

# Hosts for Heroku and local
ALLOWED_HOSTS = os.getenv(
    'ALLOWED_HOSTS',
    'localhost,127.0.0.1,trade-tracker-0f5ec3eccb7d.herokuapp.com'
).split(',')

CSRF_TRUSTED_ORIGINS = [
    "https://trade-tracker-0f5ec3eccb7d.herokuapp.com",
]

INSTRUMENT_API_KEY = os.getenv("INSTRUMENT_API_KEY")

LOGIN_URL = '/admin/login/'
LOGIN_REDIRECT_URL = 'dashboard'
LOGOUT_REDIRECT_URL = 'landing'

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    'trades',
    'crispy_forms',
    'crispy_bootstrap5',
]

CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = 'bootstrap5'

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",   # <--- Early for Heroku static
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "tradetracker.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        'DIRS': [BASE_DIR / "trades/templates"], 
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "tradetracker.wsgi.application"

# --- DATABASES ---

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}
if os.getenv("DATABASE_URL"):
    DATABASES["default"] = dj_database_url.config(conn_max_age=600, ssl_require=True)

# --- Password validation ---

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

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# --- Static files for Heroku ---
STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

X_FRAME_OPTIONS = "ALLOWALL"