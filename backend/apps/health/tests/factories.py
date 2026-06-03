"""factory_boy factories for the health app."""

from datetime import date

import factory

from apps.goats.tests.factories import GoatFactory
from apps.health.models import HealthRecord, VaccinationSchedule


class VaccinationScheduleFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = VaccinationSchedule

    vaccine_name = factory.Sequence(lambda n: f"Vaccine {n}")
    description = factory.Faker("sentence")
    interval_days = 365
    is_active = True


class HealthRecordFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = HealthRecord

    goat = factory.SubFactory(GoatFactory)
    record_type = "checkup"
    description = factory.Faker("sentence")
    record_date = factory.LazyFunction(date.today)
    # next_due_date / vaccination left null; set explicitly for vaccinations.
