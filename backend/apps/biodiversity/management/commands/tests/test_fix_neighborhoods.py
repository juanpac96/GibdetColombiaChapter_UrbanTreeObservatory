from io import StringIO

import pytest
from django.contrib.gis.geos import MultiPolygon, Point, Polygon
from django.core.management import call_command

from apps.biodiversity.models import BiodiversityRecord
from apps.places.models import Locality, Neighborhood


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

        # Create second locality with boundary for testing locality-based matching
        other_locality = Locality.objects.create(
            name="COMUNA 2",
            municipality=locality.municipality,
            boundary=MultiPolygon(Polygon.from_bbox((-75.35, 4.40, -75.30, 4.45))),
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

        # Record 3: Inside second locality but not in any neighborhood
        record_locality = BiodiversityRecord.objects.create(
            common_name="Test Tree Locality",
            species=species,
            neighborhood=unknown_neighborhood,
            location=Point(-75.32, 4.43),  # Inside other_locality boundary
            recorded_by="Test",
        )

        # Record 4: Outside both neighborhoods and localities
        record_outside = BiodiversityRecord.objects.create(
            common_name="Test Tree Outside",
            species=species,
            neighborhood=unknown_neighborhood,
            location=Point(-75.50, 4.47),  # Outside all test boundaries
            recorded_by="Test",
        )

        return {
            "unknown_neighborhood": unknown_neighborhood,
            "center_neighborhood": center_neighborhood,
            "north_neighborhood": north_neighborhood,
            "other_locality": other_locality,
            "record_center": record_center,
            "record_north": record_north,
            "record_locality": record_locality,
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
        record_locality = BiodiversityRecord.objects.get(
            id=test_data["record_locality"].id
        )
        record_outside = BiodiversityRecord.objects.get(
            id=test_data["record_outside"].id
        )

        # Check that records have been correctly assigned
        assert record_center.neighborhood.id == test_data["center_neighborhood"].id
        assert record_north.neighborhood.id == test_data["north_neighborhood"].id

        # Check locality-based record got new neighborhood
        assert record_locality.neighborhood.id != test_data["unknown_neighborhood"].id
        assert (
            record_locality.neighborhood.name
            == f"Desconocido en {test_data['other_locality'].name}"
        )
        assert (
            record_locality.neighborhood.locality.id == test_data["other_locality"].id
        )

        # Check system comments were added
        assert "Automatically assigned to neighborhood" in record_center.system_comment
        assert "Center" in record_center.system_comment
        assert "Automatically assigned to neighborhood" in record_north.system_comment
        assert "North" in record_north.system_comment
        assert "placeholder neighborhood" in record_locality.system_comment
        assert "COMUNA 2" in record_locality.system_comment

        # Check record outside boundaries gets assigned to a placeholder neighborhood
        # based on its original locality, as the point seems to be within a locality
        assert record_outside.neighborhood.name.startswith("Desconocido en")
        assert "placeholder neighborhood" in record_outside.system_comment
        assert "locality" in record_outside.system_comment

    def test_batch_processing(self, setup_test_data):
        """Test processing with small batch size."""
        test_data = setup_test_data

        # Call the command with small batch size
        out = StringIO()
        call_command(
            "fix_biodiversity_neighborhoods",
            f"--neighborhood-id={test_data['unknown_neighborhood'].id}",
            "--batch-size=1",  # Process one record at a time
            stdout=out,
        )

        # Check output
        output = out.getvalue()
        assert "Processing complete" in output

        # Verify all records were processed correctly despite small batch size
        record_center = BiodiversityRecord.objects.get(id=test_data["record_center"].id)
        record_north = BiodiversityRecord.objects.get(id=test_data["record_north"].id)
        record_locality = BiodiversityRecord.objects.get(
            id=test_data["record_locality"].id
        )
        record_outside = BiodiversityRecord.objects.get(
            id=test_data["record_outside"].id
        )

        assert record_center.neighborhood.id == test_data["center_neighborhood"].id
        assert record_north.neighborhood.id == test_data["north_neighborhood"].id
        assert record_locality.neighborhood.name.startswith("Desconocido en")
        assert (
            record_locality.neighborhood.locality.id == test_data["other_locality"].id
        )
        # Check record outside boundaries gets assigned to a placeholder neighborhood
        assert record_outside.neighborhood.name.startswith("Desconocido en")
        assert "placeholder neighborhood" in record_outside.system_comment
        assert "locality" in record_outside.system_comment

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
        record_locality = BiodiversityRecord.objects.get(
            id=test_data["record_locality"].id
        )
        record_outside = BiodiversityRecord.objects.get(
            id=test_data["record_outside"].id
        )

        # Check that records have NOT been changed
        assert record_center.neighborhood.id == test_data["unknown_neighborhood"].id
        assert record_north.neighborhood.id == test_data["unknown_neighborhood"].id
        assert record_locality.neighborhood.id == test_data["unknown_neighborhood"].id
        assert record_outside.neighborhood.id == test_data["unknown_neighborhood"].id

        # Check no system comments were added
        assert (
            record_center.system_comment is None or record_center.system_comment == ""
        )
        assert record_north.system_comment is None or record_north.system_comment == ""
        assert (
            record_locality.system_comment is None
            or record_locality.system_comment == ""
        )
        assert (
            record_outside.system_comment is None or record_outside.system_comment == ""
        )

        # Check that the placeholder neighborhood was not created
        placeholder_name = f"Desconocido en {test_data['other_locality'].name}"
        assert not Neighborhood.objects.filter(name=placeholder_name).exists()

    def test_already_processed_records(self, setup_test_data):
        """Test that records with system_comment are skipped in subsequent runs."""
        test_data = setup_test_data

        # First run - process all records
        call_command(
            "fix_biodiversity_neighborhoods",
            f"--neighborhood-id={test_data['unknown_neighborhood'].id}",
            stdout=StringIO(),
        )

        # Count records that were updated
        _ = (
            BiodiversityRecord.objects.filter(system_comment__isnull=False)
            .exclude(system_comment="")
            .count()
        )

        # Second run - should skip already processed records
        out = StringIO()
        call_command(
            "fix_biodiversity_neighborhoods",
            f"--neighborhood-id={test_data['unknown_neighborhood'].id}",
            stdout=out,
        )

        # Check output
        output = out.getvalue()
        assert (
            "Found 0 biodiversity records with unknown neighborhood to process"
            in output
        )

    def test_all_records_flag(self, setup_test_data):
        """Test that the --all-records flag processes records even if they have comments."""
        test_data = setup_test_data

        # First run - process all records
        call_command(
            "fix_biodiversity_neighborhoods",
            f"--neighborhood-id={test_data['unknown_neighborhood'].id}",
            stdout=StringIO(),
        )

        # Get one of the records and modify its comment to test reprocessing
        record_center = BiodiversityRecord.objects.get(id=test_data["record_center"].id)
        record_center.system_comment = "Modified comment for testing"
        record_center.neighborhood = test_data[
            "unknown_neighborhood"
        ]  # Reset neighborhood
        record_center.save()

        # Second run with --all-records flag
        out = StringIO()
        call_command(
            "fix_biodiversity_neighborhoods",
            f"--neighborhood-id={test_data['unknown_neighborhood'].id}",
            "--all-records",
            stdout=out,
        )

        # Check output - should find records to process
        output = out.getvalue()
        assert "Found" in output
        assert "biodiversity records with unknown neighborhood to process" in output
        assert "0 biodiversity records" not in output

        # Verify record was reprocessed
        record_center.refresh_from_db()
        assert record_center.neighborhood.id == test_data["center_neighborhood"].id
        assert "Modified comment for testing" != record_center.system_comment
        assert "Automatically assigned to neighborhood" in record_center.system_comment

        # Check output
        output = out.getvalue()
        assert "Processing complete" in output

        # Verify all records were processed correctly despite small batch size
        record_center = BiodiversityRecord.objects.get(id=test_data["record_center"].id)
        record_north = BiodiversityRecord.objects.get(id=test_data["record_north"].id)
        record_locality = BiodiversityRecord.objects.get(
            id=test_data["record_locality"].id
        )

        assert record_center.neighborhood.id == test_data["center_neighborhood"].id
        assert record_north.neighborhood.id == test_data["north_neighborhood"].id
        assert record_locality.neighborhood.name.startswith("Desconocido en")
        assert (
            record_locality.neighborhood.locality.id == test_data["other_locality"].id
        )
