"""Smoke tests — every goats factory produces a valid, persisted instance."""

import pytest

from apps.goats.models import Area, Goat
from apps.goats.tests.factories import AreaFactory, GoatFactory

pytestmark = pytest.mark.django_db


def test_area_factory_creates_valid_instance():
    area = AreaFactory()
    assert isinstance(area, Area)
    assert area.pk is not None
    assert area.capacity > 0


def test_goat_factory_creates_valid_instance():
    goat = GoatFactory()
    assert isinstance(goat, Goat)
    assert goat.pk is not None
    assert goat.tag_number
    assert goat.sex in ("M", "F")
    assert goat.status == "active"


def test_goat_factory_tag_numbers_are_unique():
    goats = GoatFactory.create_batch(3)
    tags = {g.tag_number for g in goats}
    assert len(tags) == 3
