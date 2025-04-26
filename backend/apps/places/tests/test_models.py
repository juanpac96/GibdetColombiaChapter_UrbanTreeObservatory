import pytest


@pytest.mark.django_db
def test_country_str(country):
    """Test the string representation of the country."""
    assert str(country) == country.name


@pytest.mark.django_db
def test_department_str(department):
    """Test the string representation of the department."""
    assert str(department) == f"{department.name}, {department.country.name}"


@pytest.mark.django_db
def test_municipality_str(municipality):
    """Test the string representation of the municipality."""
    assert str(municipality) == f"{municipality.name}, {municipality.department.name}"


@pytest.mark.django_db
def test_place_str(place):
    """Test the string representation of the place."""
    expected = (
        f"{place.site}, {place.municipality.name}, "
        f"{place.municipality.department.name}, "
        f"{place.municipality.department.country.name}"
    )
    assert str(place) == expected
