"""API tests for the health endpoints (records, alerts)."""

from datetime import date, timedelta

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import AccessToken

from apps.goats.tests.factories import GoatFactory
from apps.health.models import HealthRecord
from apps.health.tests.factories import (
    HealthRecordFactory,
    VaccinationScheduleFactory,
)

pytestmark = pytest.mark.django_db

User = get_user_model()
HEALTH_URL = "/api/v1/health/"
ALERTS_URL = "/api/v1/alerts/"


@pytest.fixture
def anon():
    return APIClient()


@pytest.fixture
def admin():
    user = User.objects.create_user(username="owner", password="pw")
    client = APIClient()
    client.force_authenticate(user=user)
    return client


# ── list / filter ────────────────────────────────────────────────────
def test_list_health_records_requires_auth(anon):
    assert anon.get(HEALTH_URL).status_code == 401


def test_list_health_records_filterable_by_type(admin):
    HealthRecordFactory.create_batch(2, record_type="vaccination")
    HealthRecordFactory(record_type="checkup")
    resp = admin.get(HEALTH_URL, {"record_type": "vaccination"})
    assert resp.status_code == 200
    assert resp.data["count"] == 2


def test_list_health_records_filterable_by_goat(admin):
    goat = GoatFactory()
    HealthRecordFactory(goat=goat)
    HealthRecordFactory()
    resp = admin.get(HEALTH_URL, {"goat": str(goat.id)})
    assert resp.data["count"] == 1


# ── create ───────────────────────────────────────────────────────────
def test_create_health_record_requires_auth(anon):
    goat = GoatFactory()
    resp = anon.post(
        HEALTH_URL,
        {"goat": str(goat.id), "record_type": "checkup", "record_date": "2026-01-01"},
        format="json",
    )
    assert resp.status_code == 401


def test_create_health_record_valid_returns_201(admin):
    goat = GoatFactory()
    resp = admin.post(
        HEALTH_URL,
        {"goat": str(goat.id), "record_type": "checkup", "record_date": "2026-01-01"},
        format="json",
    )
    assert resp.status_code == 201
    assert HealthRecord.objects.count() == 1


def test_create_health_record_with_schedule_computes_next_due(admin):
    goat = GoatFactory()
    schedule = VaccinationScheduleFactory(interval_days=100)
    resp = admin.post(
        HEALTH_URL,
        {
            "goat": str(goat.id),
            "record_type": "vaccination",
            "record_date": "2026-01-01",
            "vaccination": str(schedule.id),
        },
        format="json",
    )
    assert resp.status_code == 201
    assert resp.data["next_due_date"] == str(date(2026, 1, 1) + timedelta(days=100))


# ── alerts ───────────────────────────────────────────────────────────
def test_alerts_endpoint_requires_auth(anon):
    assert anon.get(ALERTS_URL).status_code == 401


def test_alerts_endpoint_returns_overdue_and_upcoming(admin):
    HealthRecordFactory(next_due_date=date.today() - timedelta(days=1))
    HealthRecordFactory(next_due_date=date.today() + timedelta(days=3))
    resp = admin.get(ALERTS_URL)
    assert resp.status_code == 200
    assert len(resp.data["overdue"]) == 1
    assert len(resp.data["due_soon"]) == 1


def test_alerts_excludes_sold_goat(admin):
    HealthRecordFactory(
        goat=GoatFactory(status="sold"),
        next_due_date=date.today() - timedelta(days=1),
    )
    resp = admin.get(ALERTS_URL)
    assert resp.data["overdue"] == []


def test_expired_access_token_returns_401(anon):
    user = User.objects.create_user(username="owner", password="pw")
    token = AccessToken.for_user(user)
    token.set_exp(lifetime=-timedelta(seconds=1))
    anon.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    assert anon.get(HEALTH_URL).status_code == 401