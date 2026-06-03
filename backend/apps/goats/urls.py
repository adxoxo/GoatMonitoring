"""Goat API routes — registered under /api/v1/ in config/urls.py."""

from rest_framework.routers import DefaultRouter

from apps.goats.views import GoatViewSet

app_name = "goats"

router = DefaultRouter()
router.register(r"goats", GoatViewSet, basename="goat")

urlpatterns = router.urls
