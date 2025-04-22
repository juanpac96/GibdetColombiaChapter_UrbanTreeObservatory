from rest_framework import serializers
from .models import Country, Department, Municipality, Place


class CountrySerializer(serializers.ModelSerializer):
    """Serializer for the Country model."""

    class Meta:
        model = Country
        fields = ["id", "name"]


class DepartmentSerializer(serializers.ModelSerializer):
    """Serializer for the Department model."""

    country = CountrySerializer(read_only=True)
    country_id = serializers.PrimaryKeyRelatedField(
        queryset=Country.objects.all(), source="country", write_only=True
    )

    class Meta:
        model = Department
        fields = ["id", "name", "country", "country_id"]


class MunicipalitySerializer(serializers.ModelSerializer):
    """Serializer for the Municipality model."""

    department = DepartmentSerializer(read_only=True)
    department_id = serializers.PrimaryKeyRelatedField(
        queryset=Department.objects.all(), source="department", write_only=True
    )

    class Meta:
        model = Municipality
        fields = ["id", "name", "department", "department_id"]


class PlaceSerializer(serializers.ModelSerializer):
    """Serializer for the Place model."""

    municipality = MunicipalitySerializer(read_only=True)
    municipality_id = serializers.PrimaryKeyRelatedField(
        queryset=Municipality.objects.all(), source="municipality", write_only=True
    )

    class Meta:
        model = Place
        fields = [
            "id",
            "uuid",
            "municipality",
            "municipality_id",
            "site",
            "populated_center",
            "zone",
            "subzone",
            "created_at",
            "updated_at",
        ]


class PlaceLightSerializer(serializers.ModelSerializer):
    """Lightweight serializer for the Place model for nested usage."""

    municipality_name = serializers.CharField(
        source="municipality.name", read_only=True
    )
    department_name = serializers.CharField(
        source="municipality.department.name", read_only=True
    )
    country_name = serializers.CharField(
        source="municipality.department.country.name", read_only=True
    )

    class Meta:
        model = Place
        fields = [
            "id",
            "uuid",
            "site",
            "municipality_name",
            "department_name",
            "country_name",
        ]
