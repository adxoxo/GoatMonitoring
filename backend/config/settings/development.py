"""Development settings — local dev via docker-compose.dev.yml or host venv."""

from .base import *  # noqa: F401,F403

DEBUG = True

# Local host dev connects to a local PostgreSQL on 127.0.0.1 (same engine as
# production — no SQLite divergence). The Docker dev stack overrides DB_HOST=db
# and the credentials via backend/.env.
DATABASES["default"]["HOST"] = env("DB_HOST", "127.0.0.1")  # noqa: F405
DATABASES["default"]["PASSWORD"] = env("DB_PASSWORD", "goatfarm")  # noqa: F405

# Permissive on the dev box only.
ALLOWED_HOSTS = ["*"]

# Let the Vite dev server (different origin) call the API in development.
CORS_ALLOWED_ORIGINS = env_list(  # noqa: F405
    "CORS_ALLOWED_ORIGINS",
    "http://localhost:5173,http://127.0.0.1:5173",
)

# Print emails to the console instead of sending them.
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
