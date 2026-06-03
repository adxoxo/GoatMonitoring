"""Seed a small, realistic demo herd for local checking.

    python manage.py seed_demo

Creates areas, goats (with QR codes + sire/dam lineage), a vaccination
schedule, and health records spanning overdue / due-soon / on-schedule.
Idempotent — re-running won't duplicate (keyed on natural fields).
"""

from datetime import date, timedelta

from django.core.management.base import BaseCommand

from apps.goats.models import Area, Goat
from apps.health.models import HealthRecord, VaccinationSchedule
from apps.qr import qrcode


class Command(BaseCommand):
    help = "Seed demo data: areas, goats (QR + lineage), and health records."

    def handle(self, *args, **options):
        does, _ = Area.objects.get_or_create(
            name="Pen A — Does", defaults={"capacity": 20}
        )
        bucks, _ = Area.objects.get_or_create(
            name="Pen B — Bucks", defaults={"capacity": 10}
        )
        nursery, _ = Area.objects.get_or_create(
            name="Nursery", defaults={"capacity": 15}
        )
        Area.objects.get_or_create(name="Quarantine", defaults={"capacity": 5})

        sire, _ = Goat.objects.get_or_create(
            tag_number="G-001",
            defaults=dict(
                name="Atlas",
                sex="M",
                current_area=bucks,
                date_of_birth=date(2022, 3, 1),
            ),
        )
        dam, _ = Goat.objects.get_or_create(
            tag_number="G-002",
            defaults=dict(
                name="Maple",
                sex="F",
                current_area=does,
                date_of_birth=date(2022, 5, 1),
            ),
        )
        # Siblings of Atlas × Maple (closely related to each other).
        kid1, _ = Goat.objects.get_or_create(
            tag_number="G-003",
            defaults=dict(
                name="Clover",
                sex="F",
                sire=sire,
                dam=dam,
                current_area=does,
                date_of_birth=date(2024, 2, 1),
            ),
        )
        kid2, _ = Goat.objects.get_or_create(
            tag_number="G-004",
            defaults=dict(
                name="Pepper",
                sex="M",
                sire=sire,
                dam=dam,
                current_area=nursery,
                date_of_birth=date(2024, 2, 1),
            ),
        )
        # Unrelated doe.
        other, _ = Goat.objects.get_or_create(
            tag_number="G-005",
            defaults=dict(
                name="Juno",
                sex="F",
                current_area=does,
                date_of_birth=date(2023, 1, 1),
            ),
        )

        goats = [sire, dam, kid1, kid2, other]
        for goat in goats:
            if not goat.qr_codes.filter(is_active=True).exists():
                qrcode.generate_qr(goat)

        ppr, _ = VaccinationSchedule.objects.get_or_create(
            vaccine_name="PPR", defaults={"interval_days": 365}
        )

        if not HealthRecord.objects.exists():
            today = date.today()
            # Overdue: vaccinated 400 days ago, next due ~35 days ago.
            HealthRecord.log(
                goat=dam,
                record_type="vaccination",
                record_date=today - timedelta(days=400),
                vaccination=ppr,
            )
            # Due soon: vaccinated 360 days ago, next due in ~5 days.
            HealthRecord.log(
                goat=kid1,
                record_type="vaccination",
                record_date=today - timedelta(days=360),
                vaccination=ppr,
            )
            # No due date (plain checkup / deworming).
            HealthRecord.log(
                goat=sire,
                record_type="checkup",
                record_date=today - timedelta(days=10),
                description="Routine check",
            )
            HealthRecord.log(
                goat=other,
                record_type="deworming",
                record_date=today - timedelta(days=5),
            )

        self.stdout.write(
            self.style.SUCCESS(
                f"Seeded {Area.objects.count()} areas, "
                f"{Goat.objects.count()} goats, "
                f"{HealthRecord.objects.count()} health records."
            )
        )
