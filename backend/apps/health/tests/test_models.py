"""Model-level tests for the health app — HealthRecord and VaccinationSchedule.

These exercise the ORM/DB contract directly (fields, choices, constraints,
relationships). Factories arrive in BUILDPLAN 1.5 for service-level tests.
"""

from datetime import date, timedelta

import pytest
from django.db import IntegrityError

from apps.goats.models import Goat
from apps.goats.tests.factories import GoatFactory
from apps.health.models import HealthRecord, VaccinationSchedule
from apps.health.tests.factories import VaccinationScheduleFactory

pytestmark = pytest.mark.django_db


def _record(goat=None, record_type="vaccination", next_due_date=None, record_date=None):
    """Helper: create a HealthRecord directly for manager/query tests."""
    return HealthRecord.objects.create(
        goat=goat or GoatFactory(),
        record_type=record_type,
        description="",
        record_date=record_date or date.today(),
        next_due_date=next_due_date,
    )


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


# ── HealthRecord manager: query helpers (BUILDPLAN 4.1) ──────────────
def test_get_by_goat_returns_ordered_records():
    goat = GoatFactory()
    older = _record(goat=goat, record_date=date(2026, 1, 1))
    newer = _record(goat=goat, record_date=date(2026, 3, 1))
    _record()  # another goat's record
    records = list(HealthRecord.objects.for_goat(goat))
    assert records == [newer, older]


def test_get_overdue_returns_records_with_past_next_due():
    rec = _record(next_due_date=date.today() - timedelta(days=1))
    assert rec in HealthRecord.objects.overdue()


def test_get_due_within_returns_records_within_days():
    soon = _record(next_due_date=date.today() + timedelta(days=3))
    far = _record(next_due_date=date.today() + timedelta(days=30))
    within = HealthRecord.objects.due_within(7)
    assert soon in within
    assert far not in within


# ── HealthRecord.log + next_due (BUILDPLAN 4.2) ──────────────────────
def test_log_record_creates_health_record():
    goat = GoatFactory()
    HealthRecord.log(
        goat=goat, record_type="checkup", description="x", record_date=date.today()
    )
    assert HealthRecord.objects.count() == 1


def test_log_with_vaccination_schedule_computes_next_due():
    goat = GoatFactory()
    schedule = VaccinationScheduleFactory(interval_days=365)
    rec = HealthRecord.log(
        goat=goat,
        record_type="vaccination",
        record_date=date(2026, 1, 10),
        vaccination=schedule,
    )
    assert rec.next_due_date == date(2026, 1, 10) + timedelta(days=365)


def test_log_without_schedule_next_due_is_none():
    rec = HealthRecord.log(
        goat=GoatFactory(), record_type="checkup", record_date=date.today()
    )
    assert rec.next_due_date is None


def test_log_record_deworming_type_accepted():
    rec = HealthRecord.log(
        goat=GoatFactory(), record_type="deworming", record_date=date.today()
    )
    assert rec.record_type == "deworming"
    assert rec.next_due_date is None


def test_get_health_summary_returns_recent_records():
    goat = GoatFactory()
    for i in range(6):
        _record(goat=goat, record_date=date(2026, 1, 1) + timedelta(days=i))
    summary = HealthRecord.recent_for(goat)
    assert len(summary) == 5


def test_get_health_summary_includes_next_due():
    goat = GoatFactory()
    _record(goat=goat, next_due_date=date.today() + timedelta(days=10))
    summary = HealthRecord.recent_for(goat)
    assert summary[0].next_due_date is not None


# ── Alerts (BUILDPLAN 4.3) ───────────────────────────────────────────
def test_get_overdue_returns_goats_with_past_due_dates():
    rec = _record(
        goat=GoatFactory(status="active"),
        next_due_date=date.today() - timedelta(days=2),
    )
    assert rec in HealthRecord.objects.overdue()


def test_get_overdue_does_not_return_future_dates():
    rec = _record(next_due_date=date.today() + timedelta(days=5))
    assert rec not in HealthRecord.objects.overdue()


def test_get_due_within_7_returns_correct_goats():
    on_boundary = _record(next_due_date=date.today() + timedelta(days=7))
    beyond = _record(next_due_date=date.today() + timedelta(days=8))
    within = HealthRecord.objects.due_within(7)
    assert on_boundary in within
    assert beyond not in within


def test_get_due_within_0_returns_only_today():
    today_rec = _record(next_due_date=date.today())
    tomorrow = _record(next_due_date=date.today() + timedelta(days=1))
    yesterday = _record(next_due_date=date.today() - timedelta(days=1))
    within = HealthRecord.objects.due_within(0)
    assert today_rec in within
    assert tomorrow not in within
    assert yesterday not in within


def test_get_dashboard_alerts_sorted_by_urgency_overdue_first():
    overdue = _record(next_due_date=date.today() - timedelta(days=1))
    due_soon = _record(next_due_date=date.today() + timedelta(days=2))
    feed = HealthRecord.objects.alerts_feed()
    assert overdue in feed["overdue"]
    assert due_soon in feed["due_soon"]


def test_get_dashboard_alerts_excludes_inactive_goats():
    sold = _record(
        goat=GoatFactory(status="sold"),
        next_due_date=date.today() - timedelta(days=1),
    )
    deceased = _record(
        goat=GoatFactory(status="deceased"),
        next_due_date=date.today() - timedelta(days=1),
    )
    quarantined = _record(
        goat=GoatFactory(status="quarantined"),
        next_due_date=date.today() - timedelta(days=1),
    )
    overdue = HealthRecord.objects.overdue()
    assert sold not in overdue
    assert deceased not in overdue
    assert quarantined in overdue


def test_overdue_excludes_null_next_due_date():
    note = _record(record_type="note", next_due_date=None)
    assert note not in HealthRecord.objects.overdue()
    assert note not in HealthRecord.objects.due_within(7)


def test_due_within_excludes_overdue():
    rec = _record(next_due_date=date.today() - timedelta(days=1))
    assert rec in HealthRecord.objects.overdue()
    assert rec not in HealthRecord.objects.due_within(7)
