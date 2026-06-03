"""Tests for goat serializers — data shaping and computed display fields."""

from datetime import date, timedelta

import pytest

from apps.goats.models import QRCode
from apps.goats.serializers import (
    GoatCreateSerializer,
    GoatProfileSerializer,
    GoatSerializer,
)
from apps.goats.tests.factories import AreaFactory, GoatFactory
from apps.health.tests.factories import HealthRecordFactory

pytestmark = pytest.mark.django_db


# ── GoatSerializer (admin list/detail) ───────────────────────────────
def test_goat_serializer_includes_display_fields():
    area = AreaFactory(name="Pen A")
    goat = GoatFactory(
        sex="F", status="active", date_of_birth=date(2024, 1, 1), current_area=area
    )
    data = GoatSerializer(goat).data
    assert data["sex_display"] == "Female"
    assert data["status_display"] == "Active"
    assert data["current_area_name"] == "Pen A"
    assert data["age_display"]  # non-empty


def test_goat_serializer_age_display_unknown_without_dob():
    goat = GoatFactory(date_of_birth=None)
    data = GoatSerializer(goat).data
    assert data["age_display"] == "Unknown"


# ── GoatProfileSerializer (public worker profile) ────────────────────
def test_profile_serializer_basic_fields():
    goat = GoatFactory(tag_number="G-777", name="Daisy", sex="F")
    data = GoatProfileSerializer(goat).data
    assert data["tag_number"] == "G-777"
    assert data["name"] == "Daisy"
    assert data["sex_display"] == "Female"


def test_profile_serializer_qr_image_url_from_active_qr():
    goat = GoatFactory()
    QRCode.objects.create(goat=goat, image_path="qr/active.png")
    data = GoatProfileSerializer(goat).data
    assert data["qr_image_url"].endswith("qr/active.png")


def test_profile_serializer_qr_image_url_is_absolute_with_request():
    from rest_framework.test import APIRequestFactory

    goat = GoatFactory()
    QRCode.objects.create(goat=goat, image_path="qr/active.png")
    request = APIRequestFactory().get("/")
    data = GoatProfileSerializer(goat, context={"request": request}).data
    # absolute (scheme+host) so the SPA on :5173 loads it from the API host
    assert data["qr_image_url"].startswith("http")
    assert data["qr_image_url"].endswith("/media/qr/active.png")


def test_profile_serializer_is_overdue_true_when_past_due():
    goat = GoatFactory()
    HealthRecordFactory(
        goat=goat,
        record_type="vaccination",
        next_due_date=date.today() - timedelta(days=1),
    )
    data = GoatProfileSerializer(goat).data
    assert data["is_overdue"] is True


def test_profile_serializer_is_overdue_false_when_future():
    goat = GoatFactory()
    HealthRecordFactory(
        goat=goat,
        record_type="vaccination",
        next_due_date=date.today() + timedelta(days=30),
    )
    data = GoatProfileSerializer(goat).data
    assert data["is_overdue"] is False


def test_profile_serializer_includes_recent_health():
    goat = GoatFactory()
    HealthRecordFactory.create_batch(2, goat=goat)
    data = GoatProfileSerializer(goat).data
    assert len(data["recent_health"]) == 2
    assert "record_type_display" in data["recent_health"][0]


def test_profile_serializer_lineage_includes_parents():
    sire = GoatFactory(sex="M", tag_number="G-SIRE")
    dam = GoatFactory(sex="F", tag_number="G-DAM")
    kid = GoatFactory(sire=sire, dam=dam)
    lineage = GoatProfileSerializer(kid).data["lineage"]
    assert lineage["sire"]["tag_number"] == "G-SIRE"
    assert lineage["dam"]["tag_number"] == "G-DAM"


def test_profile_serializer_lineage_null_parent_is_none():
    kid = GoatFactory(sire=None, dam=None)
    lineage = GoatProfileSerializer(kid).data["lineage"]
    assert lineage["sire"] is None
    assert lineage["dam"] is None


def test_profile_serializer_lineage_includes_grandparents():
    grandsire = GoatFactory(sex="M", tag_number="G-GS")
    dam = GoatFactory(sex="F", sire=grandsire)
    kid = GoatFactory(dam=dam)
    lineage = GoatProfileSerializer(kid).data["lineage"]
    assert lineage["maternal_grandsire"]["tag_number"] == "G-GS"


# ── GoatCreateSerializer ─────────────────────────────────────────────
def test_create_serializer_valid_data():
    serializer = GoatCreateSerializer(data={"tag_number": "G-NEW", "sex": "M"})
    assert serializer.is_valid(), serializer.errors


def test_create_serializer_rejects_duplicate_tag():
    GoatFactory(tag_number="G-DUP")
    serializer = GoatCreateSerializer(data={"tag_number": "G-DUP", "sex": "M"})
    assert not serializer.is_valid()
    assert "tag_number" in serializer.errors
