from django.test import TestCase
from apps.places.models import Country, Department, Municipality, Place


class CountryModelTestCase(TestCase):
    """Test case for the Country model."""

    def setUp(self):
        """Set up a country instance for testing."""
        # Note the migrations are also ran when tests are executed, 
        # so there is no need to create the country instance here.
        # self.country = Country.objects.create(name="Colombia")
        pass 

    def test_country_str(self):
        """Test the string representation of the country."""
        colombia = Country.objects.get(name="Colombia")
        self.assertEqual(str(colombia), "Colombia")

class DepartmentModelTestCase(TestCase):
    """Test case for the Department model."""

    def setUp(self):
        """Set up a department instance for testing."""
        # Note the migrations are also ran when tests are executed, 
        # so there is no need to create the department instance here.
        # colombia = Country.objects.get(name="Colombia")
        # self.department = Department.objects.create(name="Antioquia", country=colombia)
        # pass

    def test_department_str(self):
        """Test the string representation of the country."""
        department = Department.objects.get(name="Tolima")
        self.assertEqual(str(department), "Tolima, Colombia")

class MunicipalityModelTestCase(TestCase):
    """Test case for the Municipality model."""

    def setUp(self):
        """Set up a municipality instance for testing."""
        # Note the migrations are also ran when tests are executed
        # so there is no need to create the municipality instance here.
        # antioquia = Department.objects.get(name="Antioquia")
        # self.municipality = Municipality.objects.create(name="Medellín", department=antioquia)

    def test_municipality_str(self):
        """Test the string representation of the municipality."""
        municipality = Municipality.objects.get(name="Ibagué")
        self.assertEqual(str(municipality), "Ibagué, Tolima")

class PlaceModelTestCase(TestCase): 
    """Test case for the Place model."""

    def setUp(self):
        """Set up a place instance for testing."""
        municipality = Municipality.objects.get(name="Ibagué")
        self.place = Place.objects.create(
            municipality=municipality, 
            site="Parque Centenario", 
            populated_center="Ricaute", 
            zone=1, 
            subzone=2
        )

    def test_place_str(self):
        """Test the string representation of the place."""
        self.assertEqual(str(self.place), "Parque Centenario, Ibagué, Tolima, Colombia")