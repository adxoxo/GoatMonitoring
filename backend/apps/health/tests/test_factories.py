"""Smoke tests — every health factory produces a valid, persisted instance."""

import pytest

from apps.health.models import HealthRecord, VaccinationSchedule
from apps.health.tests.factories import HealthRecordFactory, VaccinationScheduleFactory

pytestmark = pytest.mark.django_db


def test_vaccination_schedule_factory_creates_valid_instance():
    schedule = VaccinationScheduleFactory()
    assert isinstance(schedule, VaccinationSchedule)
    assert schedule.pk is not None
    assert schedule.interval_days > 0
    assert schedule.is_active is True


def test_health_record_factory_creates_valid_instance():
    record = HealthRecordFactory()
    assert isinstance(record, HealthRecord)
    assert record.pk is not None
    assert record.goat.pk is not None
    assert record.record_type == "checkup"
