"""The core models are registered in Django admin (the emergency backdoor)."""

from django.contrib import admin
from django.contrib.auth import get_user_model

from apps.goats.models import Area, AreaTransferLog, Goat, QRCode
from apps.health.models import HealthRecord, VaccinationSchedule


def test_core_models_registered_in_admin():
    for model in (
        Goat,
        Area,
        QRCode,
        AreaTransferLog,
        HealthRecord,
        VaccinationSchedule,
        get_user_model(),
    ):
        assert admin.site.is_registered(model), f"{model.__name__} not registered"
