"""Tests for health serializers — display fields and derived status."""

from datetime import date, timedelta

import pytest

from apps.goats.tests.factories import GoatFactory
from apps.health.models import HealthRecord
from apps.health.serializers import (
    HealthRecordCreateSerializer,
    HealthRecordSerializer,
)
from apps.health.tests.factories import (
    HealthRecordFactory,
    VaccinationScheduleFactory,
)

pytestmark = pytest.mark.django_db


def test_health_record_serializer_includes_record_type_display():
    record = HealthRecordFactory(record_type="vaccination")
    assert HealthRecordSerializer(record).data["record_type_display"] == "Vaccination"


def test_health_record_serializer_includes_goat_tag_number():
    goat = GoatFactory(tag_number="G-321")
    record = HealthRecordFactory(goat=goat)
    assert HealthRecordSerializer(record).data["goat_tag_number"] == "G-321"


def test_health_record_serializer_vaccine_name_null_when_no_schedule():
    record = HealthRecordFactory(record_type="note", vaccination=None)
    assert HealthRecordSerializer(record).data["vaccine_name"] is None


def test_create_serializer_computes_next_due_date():
    goat = GoatFactory()
    schedule = VaccinationScheduleFactory(interval_days=200)
    serializer = HealthRecordCreateSerializer(
        data={
            "goat": str(goat.id),
            "record_type": "vaccination",
            "record_date": "2026-01-10",
            "vaccination": str(schedule.id),
        }
    )
    assert serializer.is_valid(), serializer.errors
    record = serializer.save()
    assert record.next_due_date == date(2026, 1, 10) + timedelta(days=200)


def test_health_record_serializer_status_overdue():
    record = HealthRecordFactory(next_due_date=date.today() - timedelta(days=1))
    assert HealthRecordSerializer(record).data["status"] == "overdue"


def test_health_record_serializer_status_due_soon():
    record = HealthRecordFactory(next_due_date=date.today() + timedelta(days=3))
    assert HealthRecordSerializer(record).data["status"] == "due_soon"


def test_health_record_serializer_status_on_schedule():
    record = HealthRecordFactory(next_due_date=date.today() + timedelta(days=30))
    assert HealthRecordSerializer(record).data["status"] == "on_schedule"


def test_health_record_serializer_status_none_when_no_due_date():
    record = HealthRecordFactory(next_due_date=None)
    assert HealthRecordSerializer(record).data["status"] == "none"
