"""Model-level tests for the goats app.

These test the data contract directly — fields, constraints, defaults, and
self-referential relationships — so they exercise the ORM/DB rather than going
through factories (factories arrive in BUILDPLAN 1.5 for service-level tests).
"""

import uuid
from datetime import date

import pytest
from django.db import IntegrityError

from apps.goats.models import Area, AreaTransferLog, Goat, QRCode, RiskLevel

pytestmark = pytest.mark.django_db


# ── Goat ─────────────────────────────────────────────────────────────
def test_goat_created_with_uuid_as_pk():
    goat = Goat.objects.create(tag_number="G-001", sex="F")
    assert isinstance(goat.pk, uuid.UUID)
    assert goat.id == goat.pk


def test_goat_tag_number_is_unique():
    Goat.objects.create(tag_number="G-001", sex="F")
    with pytest.raises(IntegrityError):
        Goat.objects.create(tag_number="G-001", sex="M")


def test_goat_sex_only_accepts_M_or_F():
    with pytest.raises(IntegrityError):
        Goat.objects.create(tag_number="G-002", sex="X")


def test_goat_status_defaults_to_active():
    goat = Goat.objects.create(tag_number="G-003", sex="M")
    assert goat.status == "active"


def test_goat_sire_nullable_fk_to_self():
    sire = Goat.objects.create(tag_number="G-SIRE", sex="M")
    kid = Goat.objects.create(tag_number="G-KID1", sex="F", sire=sire)
    assert kid.sire == sire
    assert kid in sire.sired_offspring.all()
    # nullable
    orphan = Goat.objects.create(tag_number="G-ORPH1", sex="F")
    assert orphan.sire is None


def test_goat_dam_nullable_fk_to_self():
    dam = Goat.objects.create(tag_number="G-DAM", sex="F")
    kid = Goat.objects.create(tag_number="G-KID2", sex="M", dam=dam)
    assert kid.dam == dam
    orphan = Goat.objects.create(tag_number="G-ORPH2", sex="M")
    assert orphan.dam is None


def test_goat_current_area_nullable_fk():
    area = Area.objects.create(name="Pen A — Does", capacity=20)
    goat = Goat.objects.create(tag_number="G-004", sex="F", current_area=area)
    assert goat.current_area == area
    unassigned = Goat.objects.create(tag_number="G-005", sex="F")
    assert unassigned.current_area is None


def test_goat_str_returns_tag_and_name():
    goat = Goat.objects.create(tag_number="G-006", name="Daisy", sex="F")
    assert str(goat) == "G-006 — Daisy"


def test_goat_date_of_birth_nullable():
    born = Goat.objects.create(
        tag_number="G-007", sex="F", date_of_birth=date(2024, 1, 1)
    )
    assert born.date_of_birth == date(2024, 1, 1)
    unknown = Goat.objects.create(tag_number="G-008", sex="F")
    assert unknown.date_of_birth is None


# ── Area ─────────────────────────────────────────────────────────────
def test_area_created_with_uuid():
    area = Area.objects.create(name="Nursery", capacity=10)
    assert isinstance(area.pk, uuid.UUID)


def test_area_capacity_is_positive_integer():
    with pytest.raises(IntegrityError):
        Area.objects.create(name="Bad Pen", capacity=0)


def test_area_str_returns_name():
    area = Area.objects.create(name="Quarantine", capacity=5)
    assert str(area) == "Quarantine"


# ── QRCode ───────────────────────────────────────────────────────────
def test_qrcode_links_to_goat():
    goat = Goat.objects.create(tag_number="G-100", sex="F")
    qr = QRCode.objects.create(goat=goat, image_path="qr/G-100.png")
    assert qr.goat == goat
    assert qr in goat.qr_codes.all()


def test_qrcode_is_active_defaults_to_true():
    goat = Goat.objects.create(tag_number="G-101", sex="F")
    qr = QRCode.objects.create(goat=goat, image_path="qr/G-101.png")
    assert qr.is_active is True


def test_only_one_active_qrcode_per_goat():
    goat = Goat.objects.create(tag_number="G-102", sex="F")
    QRCode.objects.create(goat=goat, image_path="qr/old.png")
    with pytest.raises(IntegrityError):
        QRCode.objects.create(goat=goat, image_path="qr/new.png")


def test_goat_can_have_multiple_inactive_qrcodes():
    goat = Goat.objects.create(tag_number="G-103", sex="F")
    QRCode.objects.create(goat=goat, image_path="qr/v1.png", is_active=False)
    QRCode.objects.create(goat=goat, image_path="qr/v2.png", is_active=False)
    active = QRCode.objects.create(goat=goat, image_path="qr/v3.png")
    assert goat.qr_codes.count() == 3
    assert goat.qr_codes.filter(is_active=True).count() == 1
    assert active.is_active is True


# ── AreaTransferLog ──────────────────────────────────────────────────
def test_areatransferlog_links_to_goat():
    goat = Goat.objects.create(tag_number="G-300", sex="F")
    pen_a = Area.objects.create(name="Pen A", capacity=10)
    pen_b = Area.objects.create(name="Pen B", capacity=10)
    log = AreaTransferLog.objects.create(
        goat=goat,
        from_area=pen_a,
        to_area=pen_b,
        reason="weaning",
        risk_level=RiskLevel.NONE,
        transferred_by="admin",
    )
    assert log.goat == goat
    assert log in goat.transfer_logs.all()


def test_areatransferlog_from_area_nullable():
    # First assignment has no origin pen.
    goat = Goat.objects.create(tag_number="G-301", sex="F")
    pen = Area.objects.create(name="Nursery", capacity=10)
    log = AreaTransferLog.objects.create(
        goat=goat,
        to_area=pen,
        reason="initial assignment",
        risk_level=RiskLevel.NONE,
        transferred_by="system",
    )
    assert log.from_area is None
    assert log.to_area == pen


def test_areatransferlog_risk_level_stored():
    goat = Goat.objects.create(tag_number="G-302", sex="M")
    pen = Area.objects.create(name="Pen C", capacity=10)
    log = AreaTransferLog.objects.create(
        goat=goat,
        to_area=pen,
        reason="moved next to a half-sibling",
        risk_level=RiskLevel.CLOSELY_RELATED,
        transferred_by="admin",
    )
    log.refresh_from_db()
    assert log.risk_level == RiskLevel.CLOSELY_RELATED
