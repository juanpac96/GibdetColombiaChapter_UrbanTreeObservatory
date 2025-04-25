import factory
import random
from django.contrib.gis.geos import Point
from factory.django import DjangoModelFactory
from apps.climate.models import Station, Climate
from apps.core.factories import BaseFactory
from apps.places.factories import MunicipalityFactory


class StationFactory(DjangoModelFactory):
    class Meta:
        model = Station
        django_get_or_create = ("code",)

    code = factory.Sequence(lambda n: n + 1000)  # Start from 1000
    name = factory.Sequence(lambda n: f"Weather Station {n}")

    # Generate a random point in Colombia (roughly)
    # Colombia bounds: ~(66°W to 79°W) and (~-4°S to 13°N)
    location = factory.LazyFunction(
        lambda: Point(
            random.uniform(-79.0, -66.0),  # longitude
            random.uniform(-4.0, 13.0),  # latitude
            srid=4326,
        )
    )

    municipality = factory.SubFactory(MunicipalityFactory)

    @factory.post_generation
    def ensure_municipality_consistency(self, create, extracted, **kwargs):
        """Ensure location is within municipality bounds if it's Ibagué."""
        if create and self.municipality.name == "Ibagué":
            # Ibagué bounds (approximate): -75.3W to -75.1W and 4.35N to 4.5N
            self.location = Point(
                random.uniform(-75.3, -75.1),  # longitude
                random.uniform(4.35, 4.5),  # latitude
                srid=4326,
            )
            self.save()


class ClimateFactory(BaseFactory):
    class Meta:
        model = Climate

    station = factory.SubFactory(StationFactory)
    date = factory.Faker("date_this_decade")
    sensor = factory.Iterator(
        [choice[0] for choice in Climate.SensorDescription.choices]
    )
    value = factory.Faker(
        "pyfloat", min_value=-5.0, max_value=40.0
    )  # Temperature range
    measure_unit = factory.Iterator(
        [choice[0] for choice in Climate.MeasureUnit.choices]
    )
