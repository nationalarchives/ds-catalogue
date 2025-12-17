import os

from .features import *
from .production import *
from .production import BASE_DIR, INSTALLED_APPS

ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "*").split(",")

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


ENVIRONMENT_NAME = "test"
SENTRY_SAMPLE_RATE = 0

DELIVERY_OPTIONS_API_URL = "https://delivery-options.test/data"
ROSETTA_API_URL = "https://rosetta.test/data"
WAGTAIL_API_URL = "https://wagtail.test/api/v2"
ROSETTA_ENRICHMENT_API_TIMEOUT = 5
WAGTAIL_API_TIMEOUT = 5
DELIVERY_OPTIONS_API_TIMEOUT = 5
ENRICHMENT_TIMING_ENABLED = True
ENABLE_PARALLEL_API_CALLS = True

MAX_SUBJECTS_PER_RECORD = 20
