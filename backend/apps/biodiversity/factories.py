import factory
import random
from django.contrib.gis.geos import Point
from apps.biodiversity.models import BiodiversityRecord
from apps.core.factories import BaseFactory
from apps.places.factories import PlaceFactory
from apps.taxonomy.factories import SpeciesFactory


class BiodiversityRecordFactory(BaseFactory):
    class Meta:
        model = BiodiversityRecord

    common_name = factory.Faker("word")
    species = factory.SubFactory(SpeciesFactory)
    place = factory.SubFactory(PlaceFactory)

    # Generate a random point in Colombia (roughly)
    # Colombia bounds: ~(66°W to 79°W) and (~-4°S to 13°N)
    # We use longitude, latitude order for Point
    location = factory.LazyFunction(
        lambda: Point(
            random.uniform(-79.0, -66.0),  # longitude
            random.uniform(-4.0, 13.0),  # latitude
            srid=4326,
        )
    )

    # Sometimes null to test both cases
    elevation_m = factory.Maybe(
        "with_elevation", factory.Faker("pyfloat", min_value=0, max_value=4000), None
    )
    recorded_by = factory.Faker("name")
    date = factory.Faker("date_this_decade")

    # By default, include elevation
    with_elevation = True
    municipality_name = "Ibagué"

    @factory.post_generation
    def ensure_place_consistency(self, create, extracted, **kwargs):
        """Ensure location is within specified municipality bounds if applicable."""
        municipality_name = kwargs.get("municipality_name", None)
        if create and municipality_name == "Ibagué":
            # Ibagué bounds (approximate): -75.3W to -75.1W and 4.35N to 4.5N
            self.location = Point(
                random.uniform(-75.3, -75.1),  # longitude
                random.uniform(4.35, 4.5),  # latitude
                srid=4326,
            )
            self.save()
