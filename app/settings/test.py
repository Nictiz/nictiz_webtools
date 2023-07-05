from app.settings.base import *


DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
        'ATOMIC_REQUESTS': True
    },
}


class DisableMigrations(object):

    def __contains__(self, item):
        return True

    def __getitem__(self, item):
        return None


MIGRATION_MODULES = DisableMigrations()

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
        "rq.worker": {
            "handlers": ["rq_console",],
            "level": "DEBUG"
        },
    }
}


MAPPING_TOOL_URL = 'http://localhost:8080/node/'
