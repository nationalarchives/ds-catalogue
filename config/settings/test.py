import os

from .base import *
from .base import BASE_DIR, INSTALLED_APPS
from .features import *

ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "*").split(",")

WAGTAIL_API_URL = "https://rosetta.test/data"

INSTALLED_APPS = INSTALLED_APPS + ["test"]

SECRET_KEY = "abc123"

DEBUG = True

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.path.join(BASE_DIR, "db.sqlite3"),
    }
}

# Allow integration tests to run without needing to collectstatic
# See https://docs.djangoproject.com/en/5.0/ref/contrib/staticfiles/#staticfilesstorage
STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"

ROSETTA_API_URL = "https://rosetta.test/data"

ENVIRONMENT_NAME = "test"
SENTRY_SAMPLE_RATE = 0
