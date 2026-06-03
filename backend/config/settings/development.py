"""Development settings — local dev via docker-compose.dev.yml or host venv."""

import os

from .base import *  # noqa: F401,F403

DEBUG = True

# When no external database is configured (bare host dev without Docker or a
# local PostgreSQL), fall back to a local SQLite file so makemigrations and
# migrate run anywhere. The Docker dev stack sets DB_HOST via backend/.env, so
# it keeps using PostgreSQL.
if not os.environ.get("DB_HOST"):
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",  # noqa: F405
        }
    }

# Permissive on the dev box only.
ALLOWED_HOSTS = ["*"]

# Let the Vite dev server (different origin) call the API in development.
CORS_ALLOWED_ORIGINS = env_list(  # noqa: F405
    "CORS_ALLOWED_ORIGINS",
    "http://localhost:5173,http://127.0.0.1:5173",
)

# Print emails to the console instead of sending them.
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
