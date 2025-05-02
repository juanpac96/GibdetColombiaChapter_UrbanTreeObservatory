from io import StringIO

import pytest
from django.contrib.gis.geos import MultiPolygon, Point, Polygon
from django.core.management import call_command

from apps.biodiversity.models import BiodiversityRecord
from apps.places.models import Neighborhood


@pytest.mark.django_db
class TestFixNeighborhoodsCommand:
    @pytest.fixture
    def setup_test_data(self, locality, species):
        """Create test neighborhoods and biodiversity records for testing."""
        # Create "Desconocido" neighborhood (ID will be assigned by DB)
        unknown_neighborhood = Neighborhood.objects.create(
            name="Desconocido",
            locality=locality,
            boundary=None,  # No boundary
        )

        # Create test neighborhoods with boundaries
        # Neighborhood 1: Rectangle area (approximately Ibague center)
        center_neighborhood = Neighborhood.objects.create(
            name="Center",
            locality=locality,
            boundary=MultiPolygon(Polygon.from_bbox((-75.25, 4.40, -75.20, 4.45))),
        )

        # Neighborhood 2: Rectangle area (approximately north of Ibague)
        north_neighborhood = Neighborhood.objects.create(
            name="North",
            locality=locality,
            boundary=MultiPolygon(Polygon.from_bbox((-75.25, 4.45, -75.20, 4.50))),
        )

        # Create test biodiversity records
        # Record 1: Inside center neighborhood
        record_center = BiodiversityRecord.objects.create(
            common_name="Test Tree Center",
            species=species,
            neighborhood=unknown_neighborhood,  # Initially assigned to unknown
            location=Point(-75.23, 4.43),  # Inside center neighborhood
            recorded_by="Test",
        )

        # Record 2: Inside north neighborhood
        record_north = BiodiversityRecord.objects.create(
            common_name="Test Tree North",
            species=species,
            neighborhood=unknown_neighborhood,  # Initially assigned to unknown
            location=Point(-75.23, 4.47),  # Inside north neighborhood
            recorded_by="Test",
        )

        # Record 3: Outside both neighborhoods
        record_outside = BiodiversityRecord.objects.create(
            common_name="Test Tree Outside",
            species=species,
            neighborhood=unknown_neighborhood,
            location=Point(-75.30, 4.47),  # Outside both test neighborhoods
            recorded_by="Test",
        )

        return {
            "unknown_neighborhood": unknown_neighborhood,
            "center_neighborhood": center_neighborhood,
            "north_neighborhood": north_neighborhood,
            "record_center": record_center,
            "record_north": record_north,
            "record_outside": record_outside,
        }

    def test_fix_neighborhoods(self, setup_test_data):
        """Test the fix_biodiversity_neighborhoods command."""
        test_data = setup_test_data

        # Call the command
        out = StringIO()
        call_command(
            "fix_biodiversity_neighborhoods",
            f"--neighborhood-id={test_data['unknown_neighborhood'].id}",
            stdout=out,
        )

        # Check output
        output = out.getvalue()
        assert "Processing complete" in output

        # Refresh records from database
        record_center = BiodiversityRecord.objects.get(id=test_data["record_center"].id)
        record_north = BiodiversityRecord.objects.get(id=test_data["record_north"].id)
        record_outside = BiodiversityRecord.objects.get(
            id=test_data["record_outside"].id
        )

        # Check that records have been correctly assigned
        assert record_center.neighborhood.id == test_data["center_neighborhood"].id
        assert record_north.neighborhood.id == test_data["north_neighborhood"].id
        assert record_outside.neighborhood.id == test_data["unknown_neighborhood"].id

    def test_dry_run_mode(self, setup_test_data):
        """Test that dry-run mode doesn't change the database."""
        test_data = setup_test_data

        # Call the command with dry-run
        out = StringIO()
        call_command(
            "fix_biodiversity_neighborhoods",
            f"--neighborhood-id={test_data['unknown_neighborhood'].id}",
            "--dry-run",
            stdout=out,
        )

        # Refresh records from database
        record_center = BiodiversityRecord.objects.get(id=test_data["record_center"].id)
        record_north = BiodiversityRecord.objects.get(id=test_data["record_north"].id)
        record_outside = BiodiversityRecord.objects.get(
            id=test_data["record_outside"].id
        )

        # Check that records have NOT been changed
        assert record_center.neighborhood.id == test_data["unknown_neighborhood"].id
        assert record_north.neighborhood.id == test_data["unknown_neighborhood"].id
        assert record_outside.neighborhood.id == test_data["unknown_neighborhood"].id
