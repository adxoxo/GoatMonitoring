"""Health app models — health records and vaccination schedules.

A HealthRecord captures one health event for a goat (vaccination, deworming,
checkup, etc.). When linked to a VaccinationSchedule, its ``next_due_date`` is
computed from the schedule's interval (done in the service layer, BUILDPLAN 4.2).
"""

import uuid

from django.db import models


# ── VaccinationSchedule ──────────────────────────────────────────────
class VaccinationSchedule(models.Model):
    """A reusable vaccine definition with a dosing interval. Soft-deletable."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    vaccine_name = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    interval_days = models.PositiveIntegerField(
        help_text="Days between doses — used to compute next_due_date."
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["vaccine_name"]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(interval_days__gt=0),
                name="vaccinationschedule_interval_days_positive",
            ),
        ]

    def __str__(self):
        return self.vaccine_name


# ── HealthRecord ─────────────────────────────────────────────────────
class RecordType(models.TextChoices):
    VACCINATION = "vaccination", "Vaccination"
    DEWORMING = "deworming", "Deworming"
    CHECKUP = "checkup", "Checkup"
    TREATMENT = "treatment", "Treatment"
    INJURY = "injury", "Injury"
    PREGNANCY = "pregnancy", "Pregnancy"
    NOTE = "note", "Note"


class HealthRecord(models.Model):
    """One health event logged against a goat."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    goat = models.ForeignKey(
        "goats.Goat",
        on_delete=models.CASCADE,
        related_name="health_records",
    )
    record_type = models.CharField(max_length=16, choices=RecordType.choices)
    description = models.TextField(blank=True)
    record_date = models.DateField()
    next_due_date = models.DateField(null=True, blank=True)
    administered_by = models.CharField(max_length=120, blank=True)
    vaccination = models.ForeignKey(
        VaccinationSchedule,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="health_records",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-record_date", "-created_at"]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(record_type__in=RecordType.values),
                name="healthrecord_type_valid",
            ),
        ]

    def __str__(self):
        return f"{self.goat.tag_number} — {self.record_type} ({self.record_date})"
