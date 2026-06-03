"""Tests for pen compatibility — assessing lineage risk of moving a goat into
an area already holding other goats."""

import pytest

from apps.goats.models import RiskLevel
from apps.goats.tests.factories import AreaFactory, GoatFactory

pytestmark = pytest.mark.django_db


def test_empty_area_returns_risk_none():
    candidate = GoatFactory()
    assessment = candidate.assess_area(AreaFactory())
    assert assessment.risk_level == RiskLevel.NONE
    assert assessment.related_goats == []
    assert assessment.can_proceed is True


def test_area_with_sibling_returns_closely_related():
    dam = GoatFactory(sex="F")
    area = AreaFactory()
    GoatFactory(dam=dam, current_area=area)  # resident sibling
    candidate = GoatFactory(dam=dam)
    assessment = candidate.assess_area(area)
    assert assessment.risk_level == RiskLevel.CLOSELY_RELATED


def test_area_with_unrelated_goats_returns_none():
    area = AreaFactory()
    GoatFactory.create_batch(2, current_area=area)
    candidate = GoatFactory()
    assert candidate.assess_area(area).risk_level == RiskLevel.NONE


def test_returns_list_of_related_goats():
    dam = GoatFactory(sex="F")
    area = AreaFactory()
    sibling = GoatFactory(dam=dam, current_area=area)
    GoatFactory(current_area=area)  # unrelated resident
    candidate = GoatFactory(dam=dam)
    assessment = candidate.assess_area(area)
    related_ids = [g.id for g, _ in assessment.related_goats]
    assert sibling.id in related_ids
    assert len(assessment.related_goats) == 1


def test_overall_risk_is_highest_found():
    # one closely-related (sibling) + one merely related (shared grandparent)
    dam = GoatFactory(sex="F")
    grandparent = GoatFactory(sex="F")
    parent = GoatFactory(sex="F", dam=grandparent)
    candidate_parent = GoatFactory(sex="F", dam=grandparent)
    area = AreaFactory()
    GoatFactory(dam=dam, current_area=area)  # sibling → closely related
    GoatFactory(dam=parent, current_area=area)  # cousin → related
    candidate = GoatFactory(dam=dam, sire=candidate_parent)
    assert candidate.assess_area(area).risk_level == RiskLevel.CLOSELY_RELATED


def test_can_proceed_is_always_true_even_when_closely_related():
    dam = GoatFactory(sex="F")
    area = AreaFactory()
    GoatFactory(dam=dam, current_area=area)
    candidate = GoatFactory(dam=dam)
    assert candidate.assess_area(area).can_proceed is True
