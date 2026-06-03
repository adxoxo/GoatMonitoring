"""Tests for GoatRepository — the data-access layer for the goats app.

Repositories are the only place ORM queries live. Services call these by name
and never touch ``Model.objects`` directly.
"""

import uuid

import pytest

from apps.goats.models import Goat
from apps.goats.repositories.goat_repository import GoatRepository
from apps.goats.tests.factories import AreaFactory, GoatFactory

pytestmark = pytest.mark.django_db


def test_get_by_uuid_returns_goat():
    goat = GoatFactory()
    assert GoatRepository.get_by_uuid(goat.id) == goat


def test_get_by_uuid_returns_none_if_not_found():
    assert GoatRepository.get_by_uuid(uuid.uuid4()) is None


def test_get_by_tag_returns_goat():
    goat = GoatFactory(tag_number="G-555")
    assert GoatRepository.get_by_tag("G-555") == goat


def test_get_by_tag_returns_none_if_not_found():
    assert GoatRepository.get_by_tag("NOPE") is None


def test_list_all_returns_queryset():
    GoatFactory.create_batch(3)
    result = GoatRepository.list_all()
    assert result.count() == 3


def test_list_all_filters_by_status():
    GoatFactory(status="active")
    GoatFactory(status="sold")
    result = GoatRepository.list_all({"status": "active"})
    assert result.count() == 1
    assert result.first().status == "active"


def test_list_all_filters_by_sex():
    GoatFactory(sex="F")
    GoatFactory(sex="M")
    assert GoatRepository.list_all({"sex": "M"}).count() == 1


def test_list_all_search_matches_tag_or_name():
    GoatFactory(tag_number="G-AAA", name="Daisy")
    GoatFactory(tag_number="G-BBB", name="Bella")
    assert GoatRepository.list_all({"search": "AAA"}).count() == 1
    assert GoatRepository.list_all({"search": "Bella"}).count() == 1


def test_list_by_area_returns_only_goats_in_area():
    area = AreaFactory()
    other = AreaFactory()
    GoatFactory(current_area=area)
    GoatFactory(current_area=area)
    GoatFactory(current_area=other)
    assert GoatRepository.list_by_area(area.id).count() == 2


def test_create_returns_goat_instance():
    goat = GoatRepository.create({"tag_number": "G-900", "sex": "F"})
    assert isinstance(goat, Goat)
    assert goat.pk is not None
    assert goat.tag_number == "G-900"


def test_update_changes_fields_and_returns_goat():
    goat = GoatFactory(name="Old")
    updated = GoatRepository.update(goat.id, {"name": "New"})
    updated.refresh_from_db()
    assert updated.name == "New"


def test_count_by_status_returns_counts_per_status():
    GoatFactory.create_batch(2, status="active")
    GoatFactory(status="sold")
    counts = GoatRepository.count_by_status()
    assert counts["active"] == 2
    assert counts["sold"] == 1
