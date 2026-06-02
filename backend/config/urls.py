"""
Root URL configuration.

API routes are versioned under /api/v1/ and wired per app in later phases:
    path("api/v1/", include("apps.goats.api.urls")),
    path("api/v1/", include("apps.health.api.urls")),
    path("api/v1/auth/", include("apps.users.api.urls")),

Django admin stays at /django-admin/ — emergency raw-data access only,
never linked from the UI (see CLAUDE.md).
"""

from django.contrib import admin
from django.urls import path

urlpatterns = [
    path("django-admin/", admin.site.urls),
]
