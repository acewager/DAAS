"""Development settings — local Docker Compose environment."""
import os

from .base import *  # noqa: F401,F403

DEBUG = True
EMAIL_BACKEND = os.environ.get("EMAIL_BACKEND", "django.core.mail.backends.console.EmailBackend")

INSTALLED_APPS += [  # noqa: F405
    "django_extensions",
]
