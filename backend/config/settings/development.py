"""Development settings — local dev via docker-compose.dev.yml or host venv."""

from .base import *  # noqa: F401,F403

DEBUG = True

# Permissive on the dev box only.
ALLOWED_HOSTS = ["*"]

# Let the Vite dev server (different origin) call the API in development.
CORS_ALLOWED_ORIGINS = env_list(  # noqa: F405
    "CORS_ALLOWED_ORIGINS",
    "http://localhost:5173,http://127.0.0.1:5173",
)

# Print emails to the console instead of sending them.
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
