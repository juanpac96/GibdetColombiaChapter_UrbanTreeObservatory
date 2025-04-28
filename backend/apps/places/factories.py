import factory
from factory.django import DjangoModelFactory
from apps.places.models import Country, Department, Municipality, Place
from apps.core.factories import BaseFactory


class CountryFactory(DjangoModelFactory):
    class Meta:
        model = Country
        django_get_or_create = ("name",)

    name = factory.Sequence(lambda n: f"Country {n}")


class DepartmentFactory(DjangoModelFactory):
    class Meta:
        model = Department
        django_get_or_create = ("name", "country")

    name = factory.Sequence(lambda n: f"Department {n}")
    country = factory.SubFactory(CountryFactory)


class MunicipalityFactory(DjangoModelFactory):
    class Meta:
        model = Municipality
        django_get_or_create = ("name", "department")

    name = factory.Sequence(lambda n: f"Municipality {n}")
    department = factory.SubFactory(DepartmentFactory)


class PlaceFactory(BaseFactory):
    class Meta:
        model = Place

    municipality = factory.SubFactory(MunicipalityFactory)
    site = factory.Sequence(lambda n: f"Site {n}")
    populated_center = factory.Sequence(lambda n: f"Populated Center {n}")
    zone = factory.Faker("random_int", min=1, max=10)
    subzone = factory.Faker("random_int", min=1, max=5)
