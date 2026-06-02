"""Production settings — on-premise farm server behind Nginx on the LAN."""

from django.core.exceptions import ImproperlyConfigured

from .base import *  # noqa: F401,F403

DEBUG = False

# Fail loudly rather than run production with the insecure default key.
if SECRET_KEY == "insecure-dev-key-change-me":  # noqa: F405
    raise ImproperlyConfigured("DJANGO_SECRET_KEY must be set in production.")

# ALLOWED_HOSTS comes from DJANGO_ALLOWED_HOSTS (base) — must be explicit here.
if not ALLOWED_HOSTS:  # noqa: F405
    raise ImproperlyConfigured("DJANGO_ALLOWED_HOSTS must be set in production.")

# Security hardening. Note: the farm LAN serves plain HTTP (no public TLS),
# so SSL redirect stays OFF by design — see ARCHITECTURE.md security section.
SECURE_SSL_REDIRECT = False
SECURE_CONTENT_TYPE_NOSNIFF = True
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True
X_FRAME_OPTIONS = "DENY"
