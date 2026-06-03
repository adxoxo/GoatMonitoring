"""Tests for lineage logic on the Goat model.

Ancestor traversal and relatedness risk are pure-Python model methods (no raw
SQL) — identical behaviour on SQLite and PostgreSQL, fast for a small herd.
"""

import pytest

from apps.goats.models import RiskLevel
from apps.goats.tests.factories import GoatFactory

pytestmark = pytest.mark.django_db


# ── ancestor traversal ───────────────────────────────────────────────
def test_ancestors_returns_direct_parents():
    sire = GoatFactory(sex="M")
    dam = GoatFactory(sex="F")
    kid = GoatFactory(sire=sire, dam=dam)
    assert kid.get_ancestor_ids() == {sire.id, dam.id}


def test_ancestors_depth_2_includes_grandparents():
    grandsire = GoatFactory(sex="M")
    dam = GoatFactory(sex="F", sire=grandsire)
    kid = GoatFactory(dam=dam)
    ancestors = kid.get_ancestor_ids(depth=2)
    assert dam.id in ancestors
    assert grandsire.id in ancestors


def test_ancestors_respects_depth_limit():
    ggp = GoatFactory(sex="F")
    gp = GoatFactory(sex="F", dam=ggp)
    parent = GoatFactory(sex="F", dam=gp)
    kid = GoatFactory(dam=parent)
    # depth=2 reaches grandparent but not great-grandparent
    ancestors = kid.get_ancestor_ids(depth=2)
    assert gp.id in ancestors
    assert ggp.id not in ancestors


def test_ancestors_no_parents_returns_empty():
    assert GoatFactory(sire=None, dam=None).get_ancestor_ids() == set()


def test_ancestors_does_not_include_self():
    sire = GoatFactory(sex="M")
    kid = GoatFactory(sire=sire)
    assert kid.id not in kid.get_ancestor_ids()


# ── relationship risk ────────────────────────────────────────────────
def test_full_siblings_are_closely_related():
    sire = GoatFactory(sex="M")
    dam = GoatFactory(sex="F")
    a = GoatFactory(sire=sire, dam=dam)
    b = GoatFactory(sire=sire, dam=dam)
    assert a.relationship_risk(b) == RiskLevel.CLOSELY_RELATED


def test_siblings_sharing_only_dam_are_closely_related():
    dam = GoatFactory(sex="F")
    a = GoatFactory(dam=dam)
    b = GoatFactory(dam=dam)
    assert a.relationship_risk(b) == RiskLevel.CLOSELY_RELATED


def test_siblings_sharing_only_sire_are_closely_related():
    sire = GoatFactory(sex="M")
    a = GoatFactory(sire=sire)
    b = GoatFactory(sire=sire)
    assert a.relationship_risk(b) == RiskLevel.CLOSELY_RELATED


def test_shared_grandparent_is_related():
    grandparent = GoatFactory(sex="F")
    p1 = GoatFactory(sex="F", dam=grandparent)
    p2 = GoatFactory(sex="M", dam=grandparent)
    a = GoatFactory(dam=p1)
    b = GoatFactory(sire=p2)
    assert a.relationship_risk(b) == RiskLevel.RELATED


def test_shared_depth_3_ancestor_is_related():
    ggp = GoatFactory(sex="F")
    gp1 = GoatFactory(sex="F", dam=ggp)
    gp2 = GoatFactory(sex="F", dam=ggp)
    p1 = GoatFactory(sex="F", dam=gp1)
    p2 = GoatFactory(sex="F", dam=gp2)
    a = GoatFactory(dam=p1)
    b = GoatFactory(dam=p2)
    assert a.relationship_risk(b) == RiskLevel.RELATED


def test_unrelated_goats_have_no_risk():
    a = GoatFactory(sire=GoatFactory(sex="M"), dam=GoatFactory(sex="F"))
    b = GoatFactory(sire=GoatFactory(sex="M"), dam=GoatFactory(sex="F"))
    assert a.relationship_risk(b) == RiskLevel.NONE


def test_no_parents_known_has_no_risk():
    a = GoatFactory(sire=None, dam=None)
    b = GoatFactory(sire=None, dam=None)
    assert a.relationship_risk(b) == RiskLevel.NONE


def test_parent_and_offspring_are_closely_related():
    dam = GoatFactory(sex="F")
    kid = GoatFactory(dam=dam)
    assert dam.relationship_risk(kid) == RiskLevel.CLOSELY_RELATED
    assert kid.relationship_risk(dam) == RiskLevel.CLOSELY_RELATED
