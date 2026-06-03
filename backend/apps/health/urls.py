"""Health API routes — registered under /api/v1/ in config/urls.py."""

from django.urls import path
from rest_framework.routers import DefaultRouter

from apps.health.views import (
    AlertsView,
    HealthRecordViewSet,
    VaccinationScheduleViewSet,
)

app_name = "health"

router = DefaultRouter()
router.register(r"health", HealthRecordViewSet, basename="health")
router.register(
    r"vaccination-schedules",
    VaccinationScheduleViewSet,
    basename="vaccinationschedule",
)

urlpatterns = router.urls + [
    path("alerts/", AlertsView.as_view(), name="alerts"),
]
