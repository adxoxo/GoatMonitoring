"""
Root URL configuration.

API routes are versioned under /api/v1/ and wired per app:
    path("api/v1/", include("apps.goats.urls")),
    path("api/v1/", include("apps.health.urls")),
    path("api/v1/auth/", include("apps.users.urls")),

Django admin stays at /django-admin/ — emergency raw-data access only,
never linked from the UI (see CLAUDE.md).
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("django-admin/", admin.site.urls),
    path("api/v1/auth/", include("apps.users.urls")),
    path("api/v1/", include("apps.goats.urls")),
    path("api/v1/", include("apps.health.urls")),
]

# Serve uploaded media (QR PNGs) from the Django dev server. In production
# Nginx serves /media/ directly, so this only applies when DEBUG is on.
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
