import json
from os import pardir, path

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = path.dirname(path.dirname(
    path.abspath(path.join(__file__, pardir))
))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'wm82)$7ay(ya#g788(4s#hq1w2cynlt$+2ay_noapdj-#6h7xl'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

INSTALLED_APPS = (
    'django_ethereum_events',
    'solo'
)

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': path.join(BASE_DIR, 'db.sqlite3'),
    }
}

CELERY_ALWAYS_EAGER = True

