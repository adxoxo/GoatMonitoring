"""Tests for the seed_demo management command."""

import pytest
from django.core.management import call_command

from apps.goats.models import Area, Goat
from apps.health.models import HealthRecord

pytestmark = pytest.mark.django_db


def test_seed_demo_creates_data():
    call_command("seed_demo")
    assert Area.objects.count() >= 3
    assert Goat.objects.count() >= 5
    assert HealthRecord.objects.exists()
    # at least one goat has an active QR generated
    assert Goat.objects.filter(qr_codes__is_active=True).exists()


def test_seed_demo_creates_an_overdue_record():
    call_command("seed_demo")
    assert HealthRecord.objects.overdue().exists()


def test_seed_demo_is_idempotent():
    call_command("seed_demo")
    call_command("seed_demo")
    assert Goat.objects.filter(tag_number="G-001").count() == 1
