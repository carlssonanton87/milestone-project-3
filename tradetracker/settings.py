# === TradeTracker Django settings.py ===
# All key settings for configuring security, static files, environment variables, and app integration.
# Comments are from my perspective, explaining why I did each thing.

import os
from pathlib import Path
from dotenv import load_dotenv
import dj_database_url

# Load secrets from .env file if present (great for local dev and Heroku config)
load_dotenv()

# Project base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# --- Security & Core Settings ---

# Secret key: use env var for safety, fallback to a weak key ONLY in dev!
SECRET_KEY = os.getenv("SECRET_KEY", "your-unsafe-local-dev-key")

# Debug: False in prod! Controlled by env variable
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

# Allowed hosts: safe defaults for Heroku + localhost
ALLOWED_HOSTS = os.getenv(
    "ALLOWED_HOSTS", "localhost,127.0.0.1,trade-tracker-0f5ec3eccb7d.herokuapp.com"
).split(",")

# CSRF: Trust only my deployed Heroku domain
CSRF_TRUSTED_ORIGINS = [
    "https://trade-tracker-0f5ec3eccb7d.herokuapp.com",
]

# My Alpha Vantage API key for instrument autocomplete
INSTRUMENT_API_KEY = os.getenv("INSTRUMENT_API_KEY")

# --- Authentication / Login Redirects ---

LOGIN_URL = "/admin/login/"  # Where to send non-logged-in users
LOGIN_REDIRECT_URL = "dashboard"  # After login, land on dashboard
LOGOUT_REDIRECT_URL = "landing"  # After logout, go to landing page

# --- App Registration ---
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "trades",  # My custom app
    "crispy_forms",  # For nice form layouts
    "crispy_bootstrap5",  # For Bootstrap 5 form support
]

CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# --- Middleware stack (including WhiteNoise for static files in prod) ---
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",  # Serve static files efficiently on Heroku
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# --- URL and Template config ---
ROOT_URLCONF = "tradetracker.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            BASE_DIR / "trades/templates"
        ],  # So Django can find my templates folder
        "APP_DIRS": True,  # Enable app template discovery
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
        "NAME": BASE_DIR / "db.sqlite3",  # Default for dev/testing
    }
}
# In production, use DATABASE_URL (Postgres on Heroku)
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

# --- Email config for production password reset ---
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"  # Using Gmail SMTP for password reset, etc.
EMAIL_PORT = 587
EMAIL_USE_TLS = True

EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD")
DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL", EMAIL_HOST_USER)
# (Locally, I often use console backend for dev, but production needs this config.)

# --- Internationalization ---
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# --- Static Files (CSS, JS, images) ---
STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(
    BASE_DIR, "staticfiles"
)  # Where collectstatic puts files for Heroku
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"  # Best practice for Heroku static

# --- Misc ---
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Allow iFrame embedding (e.g. for 'Am I Responsive')
X_FRAME_OPTIONS = "ALLOWALL"
