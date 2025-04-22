from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer
from apps.places.serializers import MunicipalitySerializer
from .models import Station, Climate


class StationSerializer(serializers.ModelSerializer):
    """Serializer for the Station model."""

    longitude = serializers.FloatField(read_only=True)
    latitude = serializers.FloatField(read_only=True)

    class Meta:
        model = Station
        fields = ["id", "code", "name", "location", "longitude", "latitude"]


class StationGeoSerializer(GeoFeatureModelSerializer):
    """GeoJSON serializer for the Station model."""

    class Meta:
        model = Station
        geo_field = "location"
        fields = ["id", "code", "name"]


class ClimateSerializer(serializers.ModelSerializer):
    """Serializer for the Climate model."""

    station = StationSerializer(read_only=True)
    municipality = MunicipalitySerializer(read_only=True)

    sensor_display = serializers.CharField(source="get_sensor_display", read_only=True)
    measure_unit_display = serializers.CharField(
        source="get_measure_unit_display", read_only=True
    )

    class Meta:
        model = Climate
        fields = [
            "id",
            "uuid",
            "station",
            "municipality",
            "date",
            "sensor",
            "sensor_display",
            "value",
            "measure_unit",
            "measure_unit_display",
            "created_at",
            "updated_at",
        ]
