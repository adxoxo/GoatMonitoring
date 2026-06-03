"""
Root URL configuration.

API routes are versioned under /api/v1/ and wired per app:
    path("api/v1/", include("apps.goats.urls")),
    path("api/v1/", include("apps.health.urls")),
    path("api/v1/auth/", include("apps.users.urls")),

Django admin stays at /django-admin/ — emergency raw-data access only,
never linked from the UI (see CLAUDE.md).
"""

from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("django-admin/", admin.site.urls),
    path("api/v1/auth/", include("apps.users.urls")),
    path("api/v1/", include("apps.goats.urls")),
]
