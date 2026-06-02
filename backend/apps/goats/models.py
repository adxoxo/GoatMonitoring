"""Goats app models — goat registry, areas (pens), and lineage.

A goat's UUID never changes for its lifetime (QR tags reference it). Goats are
never deleted; their ``status`` changes instead so all history is preserved.
"""

import uuid

from django.db import models


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
