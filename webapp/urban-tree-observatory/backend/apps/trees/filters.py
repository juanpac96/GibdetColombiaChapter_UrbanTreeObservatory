import django_filters
from django.db.models import Q

from .models import Tree


class TreeFilter(django_filters.FilterSet):
    """Filter for Tree model"""

    species_id = django_filters.NumberFilter(field_name="species__id")
    species_name = django_filters.CharFilter(
        field_name="species__common_name", lookup_expr="icontains"
    )

    # Filter by health status
    health_status = django_filters.ChoiceFilter(choices=Tree.HealthStatus)

    # Range filters for tree dimensions
    min_height = django_filters.NumberFilter(field_name="height", lookup_expr="gte")
    max_height = django_filters.NumberFilter(field_name="height", lookup_expr="lte")

    min_diameter = django_filters.NumberFilter(
        field_name="trunk_diameter", lookup_expr="gte"
    )
    max_diameter = django_filters.NumberFilter(
        field_name="trunk_diameter", lookup_expr="lte"
    )

    min_age = django_filters.NumberFilter(field_name="estimated_age", lookup_expr="gte")
    max_age = django_filters.NumberFilter(field_name="estimated_age", lookup_expr="lte")

    # Date range filters
    planted_after = django_filters.DateFilter(
        field_name="planting_date", lookup_expr="gte"
    )
    planted_before = django_filters.DateFilter(
        field_name="planting_date", lookup_expr="lte"
    )

    # Location filters
    neighborhood = django_filters.CharFilter(lookup_expr="icontains")

    # Native species filter
    is_native = django_filters.BooleanFilter(field_name="species__native")

    # General search
    search = django_filters.CharFilter(method="filter_search")

    def filter_search(self, queryset, name, value):
        """Custom search filter across multiple fields"""
        return queryset.filter(
            Q(uuid__icontains=value)
            | Q(address__icontains=value)
            | Q(neighborhood__icontains=value)
            | Q(species__scientific_name__icontains=value)
            | Q(species__common_name__icontains=value)
        )

    class Meta:
        model = Tree
        fields = [
            "species_id",
            "species_name",
            "health_status",
            "min_height",
            "max_height",
            "min_diameter",
            "max_diameter",
            "min_age",
            "max_age",
            "planted_after",
            "planted_before",
            "neighborhood",
            "is_native",
        ]
