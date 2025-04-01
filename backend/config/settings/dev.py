from .base import *  # noqa: F403
from .base import INSTALLED_APPS, MIDDLEWARE

# Override base settings for development
DEBUG = True

# Extra debugging tools for development
INSTALLED_APPS += [
    "debug_toolbar",
    "django_extensions",
]

MIDDLEWARE = [
    "debug_toolbar.middleware.DebugToolbarMiddleware",
] + MIDDLEWARE

# Debug toolbar settings
INTERNAL_IPS = [
    "127.0.0.1",
]

# Email configuration for development
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Disable password validation for easier testing
AUTH_PASSWORD_VALIDATORS = []

# More verbose logging
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
        "level": "INFO",
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        "django.db.backends": {
            "level": "INFO",
            "handlers": ["console"],
            "propagate": False,
        },
    },
}
