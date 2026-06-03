"""Django admin registrations for the health app (emergency backdoor)."""

from django.contrib import admin

from apps.health.models import HealthRecord, VaccinationSchedule


@admin.register(HealthRecord)
class HealthRecordAdmin(admin.ModelAdmin):
    list_display = ("goat", "record_type", "record_date", "next_due_date")
    list_filter = ("record_type",)
    raw_id_fields = ("goat", "vaccination")
    date_hierarchy = "record_date"


@admin.register(VaccinationSchedule)
class VaccinationScheduleAdmin(admin.ModelAdmin):
    list_display = ("vaccine_name", "interval_days", "is_active")
    list_filter = ("is_active",)
