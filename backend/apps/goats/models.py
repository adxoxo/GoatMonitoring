"""Goats app models — goat registry, areas (pens), and lineage.

A goat's UUID never changes for its lifetime (QR tags reference it). Goats are
never deleted; their ``status`` changes instead so all history is preserved.
"""

import uuid
from dataclasses import dataclass, field

from django.db import models


@dataclass
class PenAssessment:
    """Result of checking whether a goat can join an area (advisory only)."""

    risk_level: str
    related_goats: list = field(default_factory=list)  # [(Goat, RiskLevel), ...]
    can_proceed: bool = True  # the system advises, never blocks


# ── Area ─────────────────────────────────────────────────────────────
class Area(models.Model):
    """A physical location on the farm that holds goats (pen, nursery, etc.)."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    capacity = models.PositiveIntegerField(
        help_text="Maximum number of goats this area should hold."
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(capacity__gt=0),
                name="area_capacity_positive",
            ),
        ]

    def __str__(self):
        return self.name


# ── Goat ─────────────────────────────────────────────────────────────
class Sex(models.TextChoices):
    MALE = "M", "Male"
    FEMALE = "F", "Female"


class GoatStatus(models.TextChoices):
    ACTIVE = "active", "Active"
    SOLD = "sold", "Sold"
    DECEASED = "deceased", "Deceased"
    QUARANTINED = "quarantined", "Quarantined"


class Goat(models.Model):
    """An individual goat in the herd."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tag_number = models.CharField(max_length=32, unique=True)
    name = models.CharField(max_length=120, blank=True)
    sex = models.CharField(max_length=1, choices=Sex.choices)
    date_of_birth = models.DateField(null=True, blank=True)
    status = models.CharField(
        max_length=16,
        choices=GoatStatus.choices,
        default=GoatStatus.ACTIVE,
    )
    current_area = models.ForeignKey(
        Area,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="goats",
    )
    sire = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="sired_offspring",
    )
    dam = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="dam_offspring",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["tag_number"]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(sex__in=[Sex.MALE, Sex.FEMALE]),
                name="goat_sex_valid",
            ),
            models.CheckConstraint(
                condition=models.Q(status__in=GoatStatus.values),
                name="goat_status_valid",
            ),
        ]

    def __str__(self):
        return f"{self.tag_number} — {self.name}"

    # ── lineage ──────────────────────────────────────────────────────
    def ancestor_depths(self, depth=3):
        """Map each ancestor id → its shallowest generation distance (1..depth).

        Pure-Python walk up the sire/dam tree. Excludes self. DB-agnostic and
        fast for the herd size here (≤ 2**depth ancestors).
        """
        depths = {}
        frontier = [(self, 0)]
        while frontier:
            goat, dist = frontier.pop()
            if dist >= depth:
                continue
            for parent in (goat.sire, goat.dam):
                if parent is None:
                    continue
                nxt = dist + 1
                if parent.id not in depths or nxt < depths[parent.id]:
                    depths[parent.id] = nxt
                    frontier.append((parent, nxt))
        return depths

    def get_ancestor_ids(self, depth=3):
        return set(self.ancestor_depths(depth).keys())

    def relationship_risk(self, other, depth=3):
        """Lineage/inbreeding risk between this goat and ``other``.

        - direct ancestor/descendant, or a shared parent (full/half sibling)
          → CLOSELY_RELATED
        - any other shared ancestor within ``depth`` generations → RELATED
        - otherwise → NONE
        """
        if self.pk == other.pk:
            return RiskLevel.NONE

        mine = self.ancestor_depths(depth)
        theirs = other.ancestor_depths(depth)

        # Direct line: one is an ancestor of the other.
        if other.id in mine or self.id in theirs:
            return RiskLevel.CLOSELY_RELATED

        common = set(mine) & set(theirs)
        if not common:
            return RiskLevel.NONE

        # A shared parent (depth 1 on both sides) means siblings.
        if any(mine[anc] == 1 and theirs[anc] == 1 for anc in common):
            return RiskLevel.CLOSELY_RELATED

        return RiskLevel.RELATED

    def assess_area(self, area, depth=3):
        """Lineage risk of moving this goat into ``area`` (advisory).

        Compares this goat against every goat currently in the area and returns
        the highest risk found plus the related goats. Never blocks.
        """
        severity = [RiskLevel.NONE, RiskLevel.RELATED, RiskLevel.CLOSELY_RELATED]
        overall = RiskLevel.NONE
        related = []
        for other in area.goats.exclude(pk=self.pk):
            risk = self.relationship_risk(other, depth)
            if risk != RiskLevel.NONE:
                related.append((other, risk))
                if severity.index(risk) > severity.index(overall):
                    overall = risk
        return PenAssessment(risk_level=overall, related_goats=related)


# ── QRCode ───────────────────────────────────────────────────────────
class QRCode(models.Model):
    """A printed QR tag for a goat. Only one may be active per goat at a time.

    Regenerating a tag (lost/damaged) marks the previous QR ``is_active=False``
    and creates a new active record — the goat's UUID never changes.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    goat = models.ForeignKey(
        Goat,
        on_delete=models.CASCADE,
        related_name="qr_codes",
    )
    image_path = models.CharField(
        max_length=255,
        help_text="Path to the QR PNG, relative to MEDIA_ROOT.",
    )
    is_active = models.BooleanField(default=True)
    generated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-generated_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["goat"],
                condition=models.Q(is_active=True),
                name="one_active_qr_per_goat",
            ),
        ]

    def __str__(self):
        state = "active" if self.is_active else "inactive"
        return f"QR {self.goat.tag_number} ({state})"


# ── AreaTransferLog ──────────────────────────────────────────────────
class RiskLevel(models.TextChoices):
    """Lineage/inbreeding risk recorded at the time of a transfer."""

    NONE = "none", "None"
    RELATED = "related", "Related"
    CLOSELY_RELATED = "closely_related", "Closely related"


class AreaTransferLog(models.Model):
    """An immutable audit record of a goat being moved between areas.

    Written on every transfer regardless of risk level. The first assignment
    of a goat to an area has a null ``from_area``.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    goat = models.ForeignKey(
        Goat,
        on_delete=models.CASCADE,
        related_name="transfer_logs",
    )
    from_area = models.ForeignKey(
        Area,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="transfers_out",
    )
    to_area = models.ForeignKey(
        Area,
        on_delete=models.SET_NULL,
        null=True,
        related_name="transfers_in",
    )
    reason = models.CharField(max_length=255, blank=True)
    risk_level = models.CharField(
        max_length=16,
        choices=RiskLevel.choices,
        default=RiskLevel.NONE,
    )
    transferred_at = models.DateTimeField(auto_now_add=True)
    transferred_by = models.CharField(max_length=120)

    class Meta:
        ordering = ["-transferred_at"]

    def __str__(self):
        return (
            f"{self.goat.tag_number} → {self.to_area} ({self.transferred_at:%Y-%m-%d})"
        )
