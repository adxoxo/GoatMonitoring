"""Phase 0 scaffold sanity checks.

These verify the project wiring (settings load, apps registered, DRF/JWT
config present) — not domain behaviour. Feature tests arrive with their
features under apps/*/tests/ following RED-GREEN-REFACTOR.
"""

from django.conf import settings


def test_settings_loaded():
    assert settings.configured


def test_local_apps_registered():
    for app in ("apps.goats", "apps.health", "apps.qr", "apps.users"):
        assert app in settings.INSTALLED_APPS


def test_drf_and_jwt_configured():
    assert "rest_framework" in settings.INSTALLED_APPS
    assert "ACCESS_TOKEN_LIFETIME" in settings.SIMPLE_JWT
