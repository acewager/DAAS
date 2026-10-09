"""
Production settings.

Per 12_Deployment.md Section 23 (Production Hardening): DEBUG disabled,
HTTPS enforced, secure cookies, strong SECRET_KEY required from the
environment.
"""
from .base import *  # noqa: F401,F403

import os

DEBUG = False

# VS-061 (security review): production refuses to start without a strong,
# random SECRET_KEY — many of Django's security-critical features depend on it.
_key = os.environ.get("SECRET_KEY", "")
if not _key or len(_key) < 50 or len(set(_key)) < 10 or _key.startswith("django-insecure-"):
    raise RuntimeError(
        "SECRET_KEY must be a strong random value (50+ characters, 10+ unique) "
        "in production. Generate one with: python -c "
        "'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'"
    )

SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# VS-061: whitenoise serves Django's static files (the admin) efficiently.
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    * [
        m
        for m in MIDDLEWARE
        if m != "django.middleware.security.SecurityMiddleware"
    ],
]
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# Monitoring (M10): error tracking via Sentry when SENTRY_DSN is configured.
if os.environ.get("SENTRY_DSN"):
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration
    from sentry_sdk.integrations.celery import CeleryIntegration

    sentry_sdk.init(
        dsn=os.environ["SENTRY_DSN"],
        integrations=[DjangoIntegration(), CeleryIntegration()],
        traces_sample_rate=float(os.environ.get("SENTRY_TRACES_SAMPLE_RATE", "0.1")),
        send_default_pii=False,
    )
