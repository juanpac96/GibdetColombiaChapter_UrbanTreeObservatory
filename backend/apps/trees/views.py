from django.contrib.gis.db.models.functions import Distance as DistanceFunction
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import Distance
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .filters import TreeFilter
from .models import Maintenance, Species, Tree
from .serializers import (
    MaintenanceSerializer,
    SpeciesSerializer,
    TreeDetailSerializer,
    TreeGeoSerializer,
    TreeSerializer,
)


class SpeciesViewSet(viewsets.ModelViewSet):
    """
    API endpoint for tree species.
    """

    queryset = Species.objects.all()
    serializer_class = SpeciesSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [
        filters.SearchFilter,
        DjangoFilterBackend,
        filters.OrderingFilter,
    ]
    search_fields = ["scientific_name", "common_name", "family"]
    filterset_fields = ["native", "growth_rate"]
    ordering_fields = ["scientific_name", "common_name", "average_height"]
    ordering = ["scientific_name"]


class TreeViewSet(viewsets.ModelViewSet):
    """
    API endpoint for tree data.
    """

    queryset = Tree.objects.all().select_related("species")
    serializer_class = TreeSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [
        filters.SearchFilter,
        DjangoFilterBackend,
        filters.OrderingFilter,
    ]
    filterset_class = TreeFilter
    search_fields = [
        "uuid",
        "address",
        "neighborhood",
        "species__common_name",
        "species__scientific_name",
    ]
    ordering_fields = [
        "height",
        "trunk_diameter",
        "estimated_age",
        "health_status",
    ]
    ordering = ["species__scientific_name"]

    def get_serializer_class(self):
        if (
            self.action == "list"
            and self.request.query_params.get("format") == "geojson"
        ):
            return TreeGeoSerializer
        elif self.action == "retrieve":
            return TreeDetailSerializer
        return TreeSerializer

    @action(detail=False)
    def nearby(self, request):
        """Get trees near a specific location"""
        try:
            lat = float(request.query_params.get("lat", 0))
            lng = float(request.query_params.get("lng", 0))
            radius = float(
                request.query_params.get("radius", 500)
            )  # Default 500m radius

            user_location = Point(lng, lat, srid=4326)
            queryset = (
                Tree.objects.annotate(
                    distance=DistanceFunction("location", user_location)
                )
                .filter(location__distance_lte=(user_location, Distance(m=radius)))
                .order_by("distance")
            )

            # Paginate results
            page = self.paginate_queryset(queryset)
            if page is not None:
                if request.query_params.get("format") == "geojson":
                    serializer = TreeGeoSerializer(page, many=True)
                else:
                    serializer = TreeSerializer(page, many=True)
                return self.get_paginated_response(serializer.data)

            if request.query_params.get("format") == "geojson":
                serializer = TreeGeoSerializer(queryset, many=True)
            else:
                serializer = TreeSerializer(queryset, many=True)
            return Response(serializer.data)
        except (ValueError, TypeError):
            return Response({"error": "Invalid location parameters"}, status=400)

    @action(detail=True)
    def maintenance(self, request, pk=None):
        """Get maintenance records for a specific tree"""
        tree = self.get_object()
        maintenance = tree.maintenance_records.all().order_by("-date_performed")

        page = self.paginate_queryset(maintenance)
        if page is not None:
            serializer = MaintenanceSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = MaintenanceSerializer(maintenance, many=True)
        return Response(serializer.data)


class MaintenanceViewSet(viewsets.ModelViewSet):
    """
    API endpoint for tree maintenance records.
    """

    queryset = Maintenance.objects.all().select_related("tree", "tree__species")
    serializer_class = MaintenanceSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["tree", "maintenance_type", "date_performed"]
    ordering_fields = ["date_performed", "maintenance_type"]
    ordering = ["-date_performed"]
