from app.settings.base import *

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '+kbl$5-%8x4dn$l_cf%^^6kjb0+f5lm3rvlt56+z!)*#_^-5gm'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["localhost", "127.0.0.1"]
SESSION_COOKIE_DOMAIN = "localhost"
CSRF_COOKIE_DOMAIN = 'localhost'

CSRF_TRUSTED_ORIGINS = [
    "http://localhost:8080"
]
CORS_ORIGIN_WHITELIST = [
    "http://localhost:9123",
    "http://127.0.0.1:9123",
    "http://localhost:8080",
]
# CORS_ORIGIN_ALLOW_ALL = True
CORS_SUPPORTS_CREDENTIALS = True
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_ALL_ORIGINS = True
SESSION_COOKIE_SAMESITE=None

def show_toolbar(request):
    return True


DEBUG_TOOLBAR_CONFIG = {
    "SHOW_TOOLBAR_CALLBACK" : show_toolbar,
}

INSTALLED_APPS = ('debug_toolbar',) + INSTALLED_APPS
MIDDLEWARE     = ('debug_toolbar.middleware.DebugToolbarMiddleware',) + MIDDLEWARE
INTERNAL_IPS = [
    '127.0.0.1',
    '0.0.0.0',
    'localhost',
]
DATABASES = {
   'default': {
       'ENGINE': 'django.db.backends.postgresql_psycopg2',
       'NAME': env('POSTGRES_DB'),
       'USER': env('POSTGRES_USER'),
       'PASSWORD': env('POSTGRES_PASS'),
       'HOST': env('POSTGRES_HOST', default='postgres'),
       'PORT': env('POSTGRES_PORT', default='5432'),
   }
}
# DATABASES = {
#    'default': {
#        'ENGINE': 'django.db.backends.postgresql_psycopg2',
#        'NAME': 'tickets',
#        'USER': 'tickets',
#        'PASSWORD': 'localhost',
#        'HOST': 'postgres',
#        'PORT': '5432',
#    }
# }


## Logging configuration

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "rq_console": {
            "format": "%(asctime)s %(message)s",
            "datefmt": "%H:%M:%S",
        },
    },
    "handlers": {
        "rq_console": {
            "level": "DEBUG",
            'class': 'logging.StreamHandler',
            "formatter": "rq_console",
        },
    },
    'loggers': {
        'django.db.backends': {
            'level': 'DEBUG',
            'handlers': ['rq_console'],
        },
        "rq.worker": {
            "handlers": ["rq_console",],
            "level": "DEBUG"
        },
    }
}

MAPPING_TOOL_URL = 'http://localhost:8080/node/'

TERMINOLOGIE_USERNAME = env("TERMINOLOGIE_USERNAME")
TERMINOLOGIE_PASSWORD = env("TERMINOLOGIE_PASSWORD")
