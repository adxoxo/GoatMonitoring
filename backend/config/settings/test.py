"""Test settings — host TDD without Docker/PostgreSQL.

Dev and prod run on PostgreSQL (see base.py). This module exists only so the
test suite can run on a developer host that has neither Docker nor a local
PostgreSQL server. It swaps in an in-memory SQLite database; everything else
(apps, DRF, JWT) is inherited from development settings.

Phase 1 models and migrations are database-agnostic, so SQLite is faithful for
them. PostgreSQL-specific work (e.g. the Phase 3 recursive-CTE ancestor query)
must be tested against PostgreSQL and will revisit this choice.
"""

import tempfile

from .development import *  # noqa: F401,F403

# Keep QR PNG/PDF writes out of the repo during tests.
MEDIA_ROOT = tempfile.mkdtemp(prefix="goat-test-media-")

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

# Faster, deterministic test runs.
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]
