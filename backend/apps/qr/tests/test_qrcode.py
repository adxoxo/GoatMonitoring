"""Tests for QR generation (apps/qr/qrcode.py).

QR PNGs are written under MEDIA_ROOT; tests point MEDIA_ROOT at a tmp dir so no
real files are created.
"""

import pytest

from apps.goats.models import QRCode
from apps.goats.tests.factories import GoatFactory
from apps.qr import qrcode

pytestmark = pytest.mark.django_db


@pytest.fixture
def media_tmp(settings, tmp_path):
    settings.MEDIA_ROOT = str(tmp_path)
    return tmp_path


def test_generate_qr_creates_png_file_in_media(media_tmp):
    goat = GoatFactory()
    qrcode.generate_qr(goat)
    png = media_tmp / "qr" / f"{goat.id}.png"
    assert png.exists()
    assert png.stat().st_size > 0


def test_generate_qr_url_contains_hostname_and_uuid(settings):
    settings.FARM_LOCAL_HOSTNAME = "goatfarm.local"
    goat = GoatFactory()
    url = qrcode.qr_url(goat)
    assert "goatfarm.local" in url
    assert str(goat.id) in url
    assert url.endswith(f"/g/{goat.id}")


def test_generate_qr_creates_db_record(media_tmp):
    goat = GoatFactory()
    record = qrcode.generate_qr(goat)
    assert isinstance(record, QRCode)
    assert record.goat == goat
    assert record.is_active is True
    assert record.image_path == f"qr/{goat.id}.png"


def test_regenerate_marks_old_qr_inactive(media_tmp):
    goat = GoatFactory()
    first = qrcode.generate_qr(goat)
    second = qrcode.generate_qr(goat)
    first.refresh_from_db()
    assert first.is_active is False
    assert second.is_active is True


def test_only_one_active_qr_per_goat_after_regenerate(media_tmp):
    goat = GoatFactory()
    qrcode.generate_qr(goat)
    qrcode.generate_qr(goat)
    qrcode.generate_qr(goat)
    assert goat.qr_codes.filter(is_active=True).count() == 1
    assert goat.qr_codes.count() == 3


def test_get_print_pdf_returns_bytes(media_tmp):
    goat = GoatFactory()
    qrcode.generate_qr(goat)
    pdf = qrcode.build_print_pdf(goat)
    assert isinstance(pdf, bytes)
    assert len(pdf) > 0
    assert pdf[:4] == b"%PDF"
