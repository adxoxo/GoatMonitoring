"""DRF serializers for the goats app.

Serializers own all data shaping and computed display fields, so the frontend
renders what it receives without transforming it (see CLAUDE.md).
"""

from datetime import date

from django.conf import settings
from rest_framework import serializers

from apps.goats.models import Goat


def format_age(dob):
    """Human-readable age like ``"2y 3m"``; ``"Unknown"`` when dob is missing."""
    if not dob:
        return "Unknown"
    today = date.today()
    months = (today.year - dob.year) * 12 + (today.month - dob.month)
    if today.day < dob.day:
        months -= 1
    months = max(months, 0)
    years, rem = divmod(months, 12)
    if years and rem:
        return f"{years}y {rem}m"
    if years:
        return f"{years}y"
    return f"{rem}m"


class GoatSerializer(serializers.ModelSerializer):
    """Admin list/detail representation."""

    sex_display = serializers.CharField(source="get_sex_display", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    age_display = serializers.SerializerMethodField()
    current_area_name = serializers.CharField(
        source="current_area.name", read_only=True, default=None
    )

    class Meta:
        model = Goat
        fields = [
            "id",
            "tag_number",
            "name",
            "sex",
            "sex_display",
            "date_of_birth",
            "age_display",
            "status",
            "status_display",
            "current_area",
            "current_area_name",
            "sire",
            "dam",
            "created_at",
            "updated_at",
        ]

    def get_age_display(self, goat):
        return format_age(goat.date_of_birth)


class GoatProfileSerializer(serializers.ModelSerializer):
    """Public worker QR-scan profile — render-ready, no auth required."""

    sex_display = serializers.CharField(source="get_sex_display", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    age_display = serializers.SerializerMethodField()
    current_area_name = serializers.CharField(
        source="current_area.name", read_only=True, default=None
    )
    qr_image_url = serializers.SerializerMethodField()
    is_overdue = serializers.SerializerMethodField()
    recent_health = serializers.SerializerMethodField()

    class Meta:
        model = Goat
        fields = [
            "id",
            "tag_number",
            "name",
            "sex_display",
            "age_display",
            "status",
            "status_display",
            "current_area_name",
            "qr_image_url",
            "is_overdue",
            "recent_health",
        ]

    def get_age_display(self, goat):
        return format_age(goat.date_of_birth)

    def get_qr_image_url(self, goat):
        active = goat.qr_codes.filter(is_active=True).first()
        if not active:
            return None
        return f"{settings.MEDIA_URL}{active.image_path}"

    def get_is_overdue(self, goat):
        today = date.today()
        return goat.health_records.filter(next_due_date__lt=today).exists()

    def get_recent_health(self, goat):
        records = goat.health_records.all()[:5]
        return [
            {
                "id": str(r.id),
                "record_type": r.record_type,
                "record_type_display": r.get_record_type_display(),
                "description": r.description,
                "record_date": r.record_date,
                "next_due_date": r.next_due_date,
            }
            for r in records
        ]


class GoatCreateSerializer(serializers.ModelSerializer):
    """Admin goat registration. Unique tag_number is validated by DRF."""

    class Meta:
        model = Goat
        fields = [
            "id",
            "tag_number",
            "name",
            "sex",
            "date_of_birth",
            "status",
            "current_area",
            "sire",
            "dam",
        ]
        read_only_fields = ["id"]
