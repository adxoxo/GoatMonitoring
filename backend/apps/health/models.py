"""Health app models — health records and vaccination schedules.

A HealthRecord captures one health event for a goat (vaccination, deworming,
checkup, etc.). When linked to a VaccinationSchedule, its ``next_due_date`` is
computed from the schedule's interval. Health/alert logic lives here as a custom
manager + model methods (standard Django, no service/repository layer).
"""

import uuid
from datetime import date, timedelta

from django.db import models

# Goats with these statuses are excluded from alert feeds.
INACTIVE_GOAT_STATUSES = ("sold", "deceased")


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


class HealthRecordQuerySet(models.QuerySet):
    """Query helpers for health records and alert feeds.

    ``overdue`` and ``due_within`` are disjoint buckets keyed off
    ``next_due_date`` and exclude inactive goats by default.
    """

    def for_goat(self, goat):
        return self.filter(goat=goat)  # Meta.ordering: -record_date, -created_at

    def overdue(self, today=None, active_only=True):
        today = today or date.today()
        qs = self.filter(next_due_date__lt=today)
        if active_only:
            qs = qs.exclude(goat__status__in=INACTIVE_GOAT_STATUSES)
        return qs.order_by("next_due_date")  # most overdue first

    def due_within(self, days, today=None, active_only=True):
        today = today or date.today()
        qs = self.filter(
            next_due_date__gte=today,
            next_due_date__lte=today + timedelta(days=days),
        )
        if active_only:
            qs = qs.exclude(goat__status__in=INACTIVE_GOAT_STATUSES)
        return qs.order_by("next_due_date")

    def alerts_feed(self, days=7, today=None):
        """Overdue + due-soon, active goats only, each most-urgent-first."""
        return {
            "overdue": self.overdue(today=today),
            "due_soon": self.due_within(days, today=today),
        }


class HealthRecord(models.Model):
    """One health event logged against a goat."""

    objects = HealthRecordQuerySet.as_manager()

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

    def compute_next_due_date(self):
        """record_date + the linked schedule's interval_days, else None."""
        if self.vaccination_id and self.record_date:
            return self.record_date + timedelta(days=self.vaccination.interval_days)
        return None

    @classmethod
    def log(
        cls,
        *,
        goat,
        record_type,
        description="",
        record_date=None,
        administered_by="",
        vaccination=None,
    ):
        """Create a record, computing next_due_date from any linked schedule.

        Server-defaults ``record_date`` to today (worker logs never set it).
        """
        record = cls(
            goat=goat,
            record_type=record_type,
            description=description,
            record_date=record_date or date.today(),
            administered_by=administered_by,
            vaccination=vaccination,
        )
        record.next_due_date = record.compute_next_due_date()
        record.save()
        return record

    @classmethod
    def recent_for(cls, goat, limit=5):
        return list(cls.objects.for_goat(goat)[:limit])
