"""Model-level tests for the health app — HealthRecord and VaccinationSchedule.

These exercise the ORM/DB contract directly (fields, choices, constraints,
relationships). Factories arrive in BUILDPLAN 1.5 for service-level tests.
"""

from datetime import date, timedelta

import pytest
from django.db import IntegrityError

from apps.goats.models import Goat
from apps.health.models import HealthRecord, VaccinationSchedule

pytestmark = pytest.mark.django_db


# ── HealthRecord ─────────────────────────────────────────────────────
def test_healthrecord_links_to_goat():
    goat = Goat.objects.create(tag_number="G-200", sex="F")
    record = HealthRecord.objects.create(
        goat=goat,
        record_type="checkup",
        description="Routine check",
        record_date=date(2026, 1, 10),
    )
    assert record.goat == goat
    assert record in goat.health_records.all()


def test_healthrecord_type_choices_enforced():
    goat = Goat.objects.create(tag_number="G-201", sex="F")
    with pytest.raises(IntegrityError):
        HealthRecord.objects.create(
            goat=goat,
            record_type="not-a-real-type",
            description="bad",
            record_date=date(2026, 1, 10),
        )


def test_healthrecord_next_due_date_nullable():
    goat = Goat.objects.create(tag_number="G-202", sex="F")
    record = HealthRecord.objects.create(
        goat=goat,
        record_type="note",
        description="Observed limping",
        record_date=date(2026, 1, 10),
    )
    assert record.next_due_date is None
    record.next_due_date = date(2026, 2, 10)
    record.save()
    record.refresh_from_db()
    assert record.next_due_date == date(2026, 2, 10)


def test_healthrecord_links_to_vaccination_schedule_nullable():
    goat = Goat.objects.create(tag_number="G-203", sex="F")
    schedule = VaccinationSchedule.objects.create(vaccine_name="PPR", interval_days=365)
    record = HealthRecord.objects.create(
        goat=goat,
        record_type="vaccination",
        description="PPR dose 1",
        record_date=date(2026, 1, 10),
        next_due_date=date(2026, 1, 10) + timedelta(days=365),
        vaccination=schedule,
    )
    assert record.vaccination == schedule
    # nullable for non-vaccination records
    note = HealthRecord.objects.create(
        goat=goat,
        record_type="note",
        description="general note",
        record_date=date(2026, 1, 11),
    )
    assert note.vaccination is None


# ── VaccinationSchedule ──────────────────────────────────────────────
def test_vaccinationschedule_interval_days_positive():
    with pytest.raises(IntegrityError):
        VaccinationSchedule.objects.create(vaccine_name="Bad", interval_days=0)


def test_vaccinationschedule_soft_delete_via_is_active():
    schedule = VaccinationSchedule.objects.create(vaccine_name="FMD", interval_days=180)
    assert schedule.is_active is True
    schedule.is_active = False
    schedule.save()
    schedule.refresh_from_db()
    # Soft delete — the row still exists, just flagged inactive.
    assert schedule.is_active is False
    assert VaccinationSchedule.objects.filter(pk=schedule.pk).exists()


def test_vaccinationschedule_str_returns_vaccine_name():
    schedule = VaccinationSchedule.objects.create(
        vaccine_name="Tetanus", interval_days=730
    )
    assert str(schedule) == "Tetanus"
