"""factory_boy factories for the goats app.

Tests use these instead of ``Model.objects.create`` so valid instances are
cheap to build and relationships are wired automatically.
"""

import factory

from apps.goats.models import Area, Goat


class AreaFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Area

    name = factory.Sequence(lambda n: f"Pen {n}")
    description = factory.Faker("sentence")
    capacity = 20


class GoatFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Goat

    tag_number = factory.Sequence(lambda n: f"G-{n:04d}")
    name = factory.Faker("first_name")
    sex = factory.Iterator(["M", "F"])
    date_of_birth = factory.Faker("date_of_birth", minimum_age=0, maximum_age=8)
    # status defaults to "active" on the model.
    # current_area / sire / dam are left null; set them explicitly when needed.
