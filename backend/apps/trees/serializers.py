from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer

from .models import Maintenance, Species, Tree


class SpeciesSerializer(serializers.ModelSerializer):
    """Serializer for tree species"""

    class Meta:
        model = Species
        fields = [
            "uuid",
            "scientific_name",
            "common_name",
            "family",
            "native",
            "description",
            "average_height",
            "average_canopy_diameter",
            "growth_rate",
            "carbon_sequestration",
            "oxygen_production",
        ]


class TreeSerializer(serializers.ModelSerializer):
    """Basic serializer for tree data"""

    species_name = serializers.CharField(source="species.common_name", read_only=True)

    class Meta:
        model = Tree
        fields = [
            "uuid",
            "species",
            "species_name",
            "height",
            "trunk_diameter",
            "canopy_diameter",
            "estimated_age",
            "planting_date",
            "health_status",
            "health_notes",
            "last_inspection_date",
            "address",
            "neighborhood",
        ]


class TreeGeoSerializer(GeoFeatureModelSerializer):
    """GeoJSON serializer for tree data"""

    species_name = serializers.CharField(source="species.common_name", read_only=True)
    scientific_name = serializers.CharField(
        source="species.scientific_name", read_only=True
    )
    carbon_benefit = serializers.FloatField(read_only=True)

    class Meta:
        model = Tree
        geo_field = "location"
        fields = [
            "uuid",
            "species",
            "species_name",
            "scientific_name",
            "height",
            "trunk_diameter",
            "canopy_diameter",
            "estimated_age",
            "health_status",
            "carbon_benefit",
            "address",
            "neighborhood",
        ]


class TreeDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for tree data"""

    species = SpeciesSerializer(read_only=True)
    carbon_benefit = serializers.FloatField(read_only=True)

    class Meta:
        model = Tree
        fields = [
            "uuid",
            "species",
            "location",
            "height",
            "trunk_diameter",
            "canopy_diameter",
            "estimated_age",
            "planting_date",
            "health_status",
            "health_notes",
            "last_inspection_date",
            "address",
            "neighborhood",
            "carbon_benefit",
            "created_at",
            "updated_at",
        ]


class MaintenanceSerializer(serializers.ModelSerializer):
    """Serializer for tree maintenance records"""

    tree_uuid = serializers.CharField(source="tree.uuid", read_only=True)

    class Meta:
        model = Maintenance
        fields = [
            "tree",
            "tree_uuid",
            "maintenance_type",
            "date_performed",
            "performed_by",
            "description",
            "cost",
            "before_health",
            "after_health",
            "created_at",
        ]
