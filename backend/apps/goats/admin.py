"""Django admin registrations — emergency raw-data access only (CLAUDE.md).

Never linked from the user-facing UI. Handy for inspecting/seeding data.
"""

from django.contrib import admin

from apps.goats.models import Area, AreaTransferLog, Goat, QRCode


@admin.register(Goat)
class GoatAdmin(admin.ModelAdmin):
    list_display = ("tag_number", "name", "sex", "status", "current_area")
    list_filter = ("status", "sex")
    search_fields = ("tag_number", "name")
    raw_id_fields = ("sire", "dam", "current_area")


@admin.register(Area)
class AreaAdmin(admin.ModelAdmin):
    list_display = ("name", "capacity")
    search_fields = ("name",)


@admin.register(QRCode)
class QRCodeAdmin(admin.ModelAdmin):
    list_display = ("goat", "is_active", "generated_at")
    list_filter = ("is_active",)


@admin.register(AreaTransferLog)
class AreaTransferLogAdmin(admin.ModelAdmin):
    list_display = ("goat", "from_area", "to_area", "risk_level", "transferred_at")
    list_filter = ("risk_level",)
