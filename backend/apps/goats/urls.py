"""Goat API routes — registered under /api/v1/ in config/urls.py."""

from rest_framework.routers import DefaultRouter

from apps.goats.views import AreaViewSet, GoatViewSet

app_name = "goats"

router = DefaultRouter()
router.register(r"goats", GoatViewSet, basename="goat")
router.register(r"areas", AreaViewSet, basename="area")

urlpatterns = router.urls
