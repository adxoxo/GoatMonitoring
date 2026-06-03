"""DRF serializers for the goats app.

Serializers own all data shaping and computed display fields, so the frontend
renders what it receives without transforming it (see CLAUDE.md).
"""

from datetime import date

from django.conf import settings
from rest_framework import serializers

from apps.goats.models import Area, Goat, RiskLevel


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
    lineage = serializers.SerializerMethodField()

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
            "lineage",
        ]

    def get_age_display(self, goat):
        return format_age(goat.date_of_birth)

    def get_qr_image_url(self, goat):
        active = goat.qr_codes.filter(is_active=True).first()
        if not active:
            return None
        url = f"{settings.MEDIA_URL}{active.image_path}"
        # Absolute URL so the SPA (served from a different origin in dev) loads
        # the image from the API/media host, not its own origin.
        request = self.context.get("request")
        return request.build_absolute_uri(url) if request else url

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

    def get_lineage(self, goat):
        """Parents and grandparents (2 generations) for the lineage tree.

        Null where unknown. The frontend renders these as "Unknown".
        """

        def node(g):
            if g is None:
                return None
            return {"id": str(g.id), "tag_number": g.tag_number, "name": g.name}

        sire, dam = goat.sire, goat.dam
        return {
            "sire": node(sire),
            "dam": node(dam),
            "paternal_grandsire": node(sire.sire if sire else None),
            "paternal_granddam": node(sire.dam if sire else None),
            "maternal_grandsire": node(dam.sire if dam else None),
            "maternal_granddam": node(dam.dam if dam else None),
        }


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


class AreaSerializer(serializers.ModelSerializer):
    """Area (pen) with a live count of the goats currently assigned to it."""

    goat_count = serializers.IntegerField(source="goats.count", read_only=True)

    class Meta:
        model = Area
        fields = ["id", "name", "description", "capacity", "goat_count", "created_at"]
        read_only_fields = ["id", "created_at"]


class GoatTransferSerializer(serializers.Serializer):
    """Output for a transfer: goat, risk level, audit log, and related goats."""

    goat = serializers.SerializerMethodField()
    risk_level = serializers.SerializerMethodField()
    risk_level_display = serializers.SerializerMethodField()
    transfer_log = serializers.SerializerMethodField()
    related_goats = serializers.SerializerMethodField()

    def get_goat(self, result):
        goat = result.goat
        return {
            "id": str(goat.id),
            "tag_number": goat.tag_number,
            "current_area": str(goat.current_area_id) if goat.current_area_id else None,
        }

    def get_risk_level(self, result):
        return result.assessment.risk_level

    def get_risk_level_display(self, result):
        return RiskLevel(result.assessment.risk_level).label

    def get_transfer_log(self, result):
        log = result.log
        return {
            "id": str(log.id),
            "from_area": str(log.from_area_id) if log.from_area_id else None,
            "to_area": str(log.to_area_id),
            "reason": log.reason,
            "transferred_at": log.transferred_at,
            "transferred_by": log.transferred_by,
        }

    def get_related_goats(self, result):
        return [
            {
                "id": str(goat.id),
                "tag_number": goat.tag_number,
                "name": goat.name,
                "risk_level": risk,
            }
            for goat, risk in result.assessment.related_goats
        ]
