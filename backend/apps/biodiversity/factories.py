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

    @factory.post_generation
    def set_location_for_specific_municipalities(self, create, extracted, **kwargs):
        """Set location coordinates appropriate for the place's municipality if needed.

        This is a hook for tests to ensure geographic consistency when required.
        """
        if not create:
            return

        # Municipality locations can be added when specific tests need them
        municipality_bounds = {
            "Ibagué": {
                "lon_min": -75.3,
                "lon_max": -75.1,
                "lat_min": 4.35,
                "lat_max": 4.5,
            }
            # Add other municipalities as needed for tests
        }

        # Use municipality name from kwargs if provided, otherwise check the place
        municipality_name = kwargs.get("municipality_name", None)
        if municipality_name is None and self.place and self.place.municipality:
            municipality_name = self.place.municipality.name

        if municipality_name in municipality_bounds:
            bounds = municipality_bounds[municipality_name]
            self.location = Point(
                random.uniform(bounds["lon_min"], bounds["lon_max"]),
                random.uniform(bounds["lat_min"], bounds["lat_max"]),
                srid=4326,
            )
            self.save()
