"""Test settings.

Inherits the development PostgreSQL connection so tests run on the same engine
as dev and production (pytest-django creates/drops a ``test_<dbname>`` database;
the DB role needs CREATEDB). Only test-specific tweaks live here.
"""

import tempfile

from .development import *  # noqa: F401,F403

# Keep QR PNG/PDF writes out of the repo during tests.
MEDIA_ROOT = tempfile.mkdtemp(prefix="goat-test-media-")

# Faster, deterministic test runs.
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]
