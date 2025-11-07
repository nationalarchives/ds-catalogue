import json
import os
from sysconfig import get_path

from config.util import strtobool
from csp.constants import NONE, SELF

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_DIR = os.path.dirname(PROJECT_DIR)

ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "").split(",")

# Application definition
INSTALLED_APPS = [
    "app.records",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "csp",
]

MIDDLEWARE = [
    "app.errors.middleware.CustomExceptionMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "csp.middleware.CSPMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.jinja2.Jinja2",
        "DIRS": [
            os.path.join(BASE_DIR, "app/templates"),
            os.path.join(get_path("platlib"), "tna_frontend_jinja/templates"),
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "environment": "config.jinja2.environment",
        },
    },
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
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

# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.path.join(BASE_DIR, "db.sqlite3"),
    }
}

# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

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

# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = "catalogue/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "static")
STATICFILES_DIRS = [os.path.join(BASE_DIR, "app", "static")]
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# TNA Configuration

CONTAINER_IMAGE: str = os.environ.get("CONTAINER_IMAGE", "")
BUILD_VERSION: str = os.environ.get("BUILD_VERSION", "")
TNA_FRONTEND_VERSION: str = ""
try:
    with open(
        os.path.join(
            os.path.realpath(os.path.dirname(__file__)),
            "node_modules/@nationalarchives/frontend",
            "package.json",
        )
    ) as package_json:
        try:
            data = json.load(package_json)
            TNA_FRONTEND_VERSION = data["version"] or ""
        except ValueError:
            pass
except FileNotFoundError:
    pass

WAGTAIL_API_URL: str = os.getenv("WAGTAIL_API_URL", "")
WAGTAIL_HOME_PAGE_ID: int = 3
WAGTAIL_EXPLORE_THE_COLLECTION_PAGE_ID: int = 5
WAGTAIL_EXPLORE_THE_COLLECTION_STORIES_PAGE_ID: int = 55

SECRET_KEY: str = os.environ.get("SECRET_KEY", "")

DEBUG: bool = strtobool(os.getenv("DEBUG", "False"))

COOKIE_DOMAIN: str = os.environ.get("COOKIE_DOMAIN", "")

CSP_REPORT_URL: str = os.environ.get("CSP_REPORT_URL", "")
if CSP_REPORT_URL:
    CSP_REPORT_URL += (
        f"&sentry_release={BUILD_VERSION}" if BUILD_VERSION else ""
    )
CONTENT_SECURITY_POLICY = {
    "DIRECTIVES": {
        "default-src": [SELF],
        "base-uri": [NONE],
        "object-src": [NONE],
        "img-src": os.environ.get("CSP_IMG_SRC", SELF).split(","),
        "script-src": os.environ.get("CSP_SCRIPT_SRC", SELF).split(","),
        "style-src": os.environ.get("CSP_STYLE_SRC", SELF).split(","),
        "font-src": os.environ.get("CSP_FONT_SRC", SELF).split(","),
        "connect-src": os.environ.get("CSP_CONNECT_SRC", SELF).split(","),
        "media-src": os.environ.get("CSP_MEDIA_SRC", SELF).split(","),
        "worker-src": os.environ.get("CSP_WORKER_SRC", SELF).split(","),
        "frame-src": os.environ.get("CSP_FRAME_SRC", SELF).split(","),
        "report-uri": CSP_REPORT_URL or None,
    }
}

GA4_ID = os.environ.get("GA4_ID", "")

ROSETTA_API_URL = os.getenv("ROSETTA_API_URL")

# Maximum number of subject/article_tags returned from Wagtail
MAX_SUBJECTS_PER_RECORD: int = int(os.getenv("MAX_SUBJECTS_PER_RECORD", 20))
WAGTAIL_API_TIMEOUT: int = int(os.getenv("WAGTAIL_API_TIMEOUT", 5))

# DORIS is TNA's Document Ordering System that contains Delivery Options data
DELIVERY_OPTIONS_API_URL = os.getenv("DELIVERY_OPTIONS_API_URL")

# List of IP address for identifying staff members within the organisation
STAFFIN_IP_ADDRESSES = list(
    filter(None, os.getenv("STAFFIN_IP_ADDRESSES", "").split(","))
)

# List of IP address for identifying on-site public users
ONSITE_IP_ADDRESSES = list(
    filter(None, os.getenv("ONSITE_IP_ADDRESSES", "").split(","))
)

# List of Distressing content prefixes
DCS_PREFIXES = list(filter(None, os.getenv("DCS_PREFIXES", "").split(",")))

# Should always be True in production
CLIENT_VERIFY_CERTIFICATES = strtobool(
    os.getenv("ROSETTA_CLIENT_VERIFY_CERTIFICATES", "True")
)

# logging
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "WARNING",
    },
}

SENTRY_DSN = os.getenv("SENTRY_DSN", "")
ENVIRONMENT_NAME = os.getenv("ENVIRONMENT_NAME", "production")
SENTRY_SAMPLE_RATE = float(os.getenv("SENTRY_SAMPLE_RATE", "0.1"))

ADVANCED_DOCUMENT_ORDER_EMAIL = os.getenv(
    "ADVANCED_DOCUMENT_ORDER_EMAIL",
    "advanceddocumentorder@nationalarchives.gov.uk",
)

# Image library URL
IMAGE_LIBRARY_URL = os.getenv(
    "IMAGE_LIBRARY_URL", "https://images.nationalarchives.gov.uk/"
)

# Generated in the CI/CD process
BUILD_VERSION = os.getenv("BUILD_VERSION", "")
