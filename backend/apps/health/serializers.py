"""DRF serializers for the health app.

Serializers own all data shaping and computed display fields (see CLAUDE.md):
record_type_display, goat_tag_number, vaccine_name, and a derived ``status``
(overdue / due_soon / on_schedule / none) so the frontend renders, never computes.
"""

from datetime import date, timedelta

from rest_framework import serializers

from apps.health.models import HealthRecord, VaccinationSchedule

DUE_SOON_DAYS = 7


class VaccinationScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = VaccinationSchedule
        fields = ["id", "vaccine_name", "description", "interval_days", "is_active"]
        read_only_fields = ["id"]


class HealthRecordSerializer(serializers.ModelSerializer):
    """Admin list/detail + alerts representation — fully render-ready."""

    record_type_display = serializers.CharField(
        source="get_record_type_display", read_only=True
    )
    goat_tag_number = serializers.CharField(source="goat.tag_number", read_only=True)
    vaccine_name = serializers.CharField(
        source="vaccination.vaccine_name", read_only=True, default=None
    )
    status = serializers.SerializerMethodField()

    class Meta:
        model = HealthRecord
        fields = [
            "id",
            "goat",
            "goat_tag_number",
            "record_type",
            "record_type_display",
            "description",
            "record_date",
            "next_due_date",
            "administered_by",
            "vaccination",
            "vaccine_name",
            "status",
            "created_at",
        ]
        read_only_fields = ["id", "next_due_date", "created_at"]

    def get_status(self, record):
        if record.next_due_date is None:
            return "none"
        today = date.today()
        if record.next_due_date < today:
            return "overdue"
        if record.next_due_date <= today + timedelta(days=DUE_SOON_DAYS):
            return "due_soon"
        return "on_schedule"


class HealthRecordCreateSerializer(serializers.ModelSerializer):
    """Admin health-record logging. next_due_date is computed by the model."""

    class Meta:
        model = HealthRecord
        fields = [
            "id",
            "goat",
            "record_type",
            "description",
            "record_date",
            "administered_by",
            "vaccination",
        ]
        read_only_fields = ["id"]

    def create(self, validated_data):
        return HealthRecord.log(**validated_data)


class WorkerHealthLogSerializer(serializers.ModelSerializer):
    """Public worker quick-note. ``goat`` is injected by the view via
    ``.save(goat=...)``; record_date is server-defaulted to today."""

    class Meta:
        model = HealthRecord
        fields = ["id", "record_type", "description", "record_date"]
        read_only_fields = ["id"]
        extra_kwargs = {
            "record_date": {"required": False},
            "description": {"required": False},
        }

    def create(self, validated_data):
        return HealthRecord.log(**validated_data)
