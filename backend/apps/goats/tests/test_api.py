"""API tests for the goat registry endpoints (GoatViewSet)."""

from datetime import date, timedelta

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import AccessToken

from apps.goats.models import AreaTransferLog, Goat
from apps.goats.tests.factories import AreaFactory, GoatFactory
from apps.health.models import HealthRecord

pytestmark = pytest.mark.django_db

User = get_user_model()
LIST_URL = "/api/v1/goats/"


def detail_url(goat_id):
    return f"/api/v1/goats/{goat_id}/"


@pytest.fixture
def anon():
    return APIClient()


@pytest.fixture
def admin():
    user = User.objects.create_user(username="owner", password="pw")
    client = APIClient()
    client.force_authenticate(user=user)
    return client


# ── public worker profile ────────────────────────────────────────────
def test_get_goat_profile_public_returns_200(anon):
    goat = GoatFactory(tag_number="G-1")
    resp = anon.get(detail_url(goat.id))
    assert resp.status_code == 200
    assert resp.data["tag_number"] == "G-1"
    assert "recent_health" in resp.data


def test_get_goat_profile_unknown_uuid_returns_404(anon):
    import uuid

    resp = anon.get(detail_url(uuid.uuid4()))
    assert resp.status_code == 404


# ── list (admin) ─────────────────────────────────────────────────────
def test_list_goats_requires_auth(anon):
    resp = anon.get(LIST_URL)
    assert resp.status_code == 401


def test_list_goats_returns_paginated_results(admin):
    GoatFactory.create_batch(3)
    resp = admin.get(LIST_URL)
    assert resp.status_code == 200
    assert "results" in resp.data
    assert resp.data["count"] == 3


def test_list_goats_filter_by_status(admin):
    GoatFactory(status="active")
    GoatFactory(status="sold")
    resp = admin.get(LIST_URL, {"status": "sold"})
    assert resp.data["count"] == 1


# ── create (admin) ───────────────────────────────────────────────────
def test_create_goat_requires_auth(anon):
    resp = anon.post(LIST_URL, {"tag_number": "G-X", "sex": "F"}, format="json")
    assert resp.status_code == 401


def test_create_goat_valid_data_returns_201(admin):
    resp = admin.post(LIST_URL, {"tag_number": "G-100", "sex": "F"}, format="json")
    assert resp.status_code == 201
    assert Goat.objects.filter(tag_number="G-100").exists()


def test_create_goat_duplicate_tag_returns_400(admin):
    GoatFactory(tag_number="G-DUP")
    resp = admin.post(LIST_URL, {"tag_number": "G-DUP", "sex": "M"}, format="json")
    assert resp.status_code == 400


def test_create_goat_triggers_qr_generation(admin):
    resp = admin.post(LIST_URL, {"tag_number": "G-QR", "sex": "F"}, format="json")
    assert resp.status_code == 201
    goat = Goat.objects.get(tag_number="G-QR")
    assert goat.qr_codes.filter(is_active=True).count() == 1


# ── update (admin) ───────────────────────────────────────────────────
def test_patch_goat_updates_name(admin):
    goat = GoatFactory(name="Old")
    resp = admin.patch(detail_url(goat.id), {"name": "New"}, format="json")
    assert resp.status_code == 200
    goat.refresh_from_db()
    assert goat.name == "New"


# ── regenerate QR action (admin) ─────────────────────────────────────
def test_regenerate_qr_marks_old_inactive(admin):
    goat = GoatFactory()
    admin.post(f"{detail_url(goat.id)}qr/")
    admin.post(f"{detail_url(goat.id)}qr/")
    assert goat.qr_codes.count() == 2
    assert goat.qr_codes.filter(is_active=True).count() == 1


def test_regenerate_qr_requires_auth(anon):
    goat = GoatFactory()
    resp = anon.post(f"{detail_url(goat.id)}qr/")
    assert resp.status_code == 401


# ── areas ────────────────────────────────────────────────────────────
AREAS_URL = "/api/v1/areas/"


def test_list_areas_requires_auth(anon):
    assert anon.get(AREAS_URL).status_code == 401


def test_list_areas_returns_areas(admin):
    AreaFactory.create_batch(2)
    resp = admin.get(AREAS_URL)
    assert resp.status_code == 200
    assert resp.data["count"] == 2


def test_create_area(admin):
    resp = admin.post(AREAS_URL, {"name": "Pen A", "capacity": 20}, format="json")
    assert resp.status_code == 201


def test_area_serializer_includes_goat_count(admin):
    area = AreaFactory()
    GoatFactory.create_batch(2, current_area=area)
    resp = admin.get(f"{AREAS_URL}{area.id}/")
    assert resp.data["goat_count"] == 2


# ── transfer ─────────────────────────────────────────────────────────
def transfer_url(goat_id):
    return f"/api/v1/goats/{goat_id}/transfer/"


def test_transfer_requires_auth(anon):
    goat = GoatFactory()
    area = AreaFactory()
    resp = anon.post(
        transfer_url(goat.id), {"target_area_id": str(area.id)}, format="json"
    )
    assert resp.status_code == 401


def test_transfer_to_valid_area_returns_200_with_risk_level(admin):
    goat = GoatFactory()
    area = AreaFactory()
    resp = admin.post(
        transfer_url(goat.id), {"target_area_id": str(area.id)}, format="json"
    )
    assert resp.status_code == 200
    assert resp.data["risk_level"] == "none"


def test_transfer_to_area_with_sibling_returns_closely_related(admin):
    dam = GoatFactory(sex="F")
    area = AreaFactory()
    GoatFactory(dam=dam, current_area=area)  # resident sibling
    candidate = GoatFactory(dam=dam)
    resp = admin.post(
        transfer_url(candidate.id), {"target_area_id": str(area.id)}, format="json"
    )
    assert resp.data["risk_level"] == "closely_related"
    assert len(resp.data["related_goats"]) == 1


def test_transfer_writes_log_and_updates_area(admin):
    goat = GoatFactory()
    area = AreaFactory()
    admin.post(
        transfer_url(goat.id),
        {"target_area_id": str(area.id), "reason": "weaning"},
        format="json",
    )
    goat.refresh_from_db()
    assert goat.current_area == area
    log = AreaTransferLog.objects.get(goat=goat)
    assert log.to_area == area
    assert log.reason == "weaning"


def test_transfer_to_unknown_area_returns_404(admin):
    import uuid

    goat = GoatFactory()
    resp = admin.post(
        transfer_url(goat.id), {"target_area_id": str(uuid.uuid4())}, format="json"
    )
    assert resp.status_code == 404


# ── worker health log (public) ───────────────────────────────────────
def log_url(goat_id):
    return f"/api/v1/goats/{goat_id}/log/"


def test_worker_log_endpoint_public_no_auth_required(anon):
    goat = GoatFactory()
    resp = anon.post(
        log_url(goat.id),
        {"record_type": "note", "description": "Limping"},
        format="json",
    )
    assert resp.status_code == 201


def test_worker_log_endpoint_creates_health_record(anon):
    goat = GoatFactory()
    anon.post(
        log_url(goat.id),
        {"record_type": "note", "description": "Limping"},
        format="json",
    )
    assert HealthRecord.objects.filter(goat=goat).count() == 1


def test_worker_log_record_date_defaults_to_today(anon):
    goat = GoatFactory()
    anon.post(log_url(goat.id), {"record_type": "note"}, format="json")
    assert HealthRecord.objects.get(goat=goat).record_date == date.today()


def test_worker_log_invalid_record_type_returns_400(anon):
    goat = GoatFactory()
    resp = anon.post(log_url(goat.id), {"record_type": "bogus"}, format="json")
    assert resp.status_code == 400


# ── expired token ────────────────────────────────────────────────────
def test_expired_access_token_returns_401(anon):
    user = User.objects.create_user(username="owner", password="pw")
    token = AccessToken.for_user(user)
    token.set_exp(lifetime=-timedelta(seconds=1))
    anon.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    resp = anon.get(LIST_URL)
    assert resp.status_code == 401
