"""
Tests for the mapping utilities in the core app.
"""

from django.test import TestCase

from apps.taxonomy.models import Species
from apps.reports.models import Measurement, Observation
from apps.core.utils.mappings import (
    get_mapped_value,
    ORIGIN_MAPPINGS,
    IUCN_STATUS_MAPPINGS,
    LIFEFORM_MAPPINGS,
    MEASURED_ATTRIBUTE_MAPPINGS,
    MEASUREMENT_UNIT_MAPPINGS,
    REPRODUCTIVE_CONDITION_MAPPINGS,
    PHYTOSANITARY_STATUS_MAPPINGS,
)


class MappingUtilsTestCase(TestCase):
    """Test case for the mapping utilities."""

    def test_get_mapped_value_exact_match(self):
        """Test that an exact match returns the correct value."""
        self.assertEqual(
            get_mapped_value("Exótica", ORIGIN_MAPPINGS), Species.Origin.EXOTIC
        )

    def test_get_mapped_value_case_insensitive(self):
        """Test that case-insensitive matching works."""
        self.assertEqual(
            get_mapped_value("exótica", ORIGIN_MAPPINGS), Species.Origin.EXOTIC
        )

    def test_get_mapped_value_default(self):
        """Test that the default value is returned for non-matches."""
        self.assertEqual(
            get_mapped_value("Unknown", ORIGIN_MAPPINGS, default="DEFAULT"), "DEFAULT"
        )

    def test_get_mapped_value_none_input(self):
        """Test that None input returns the default value."""
        self.assertEqual(
            get_mapped_value(None, ORIGIN_MAPPINGS, default="DEFAULT"), "DEFAULT"
        )

    def test_origin_mappings(self):
        """Test that origin mappings work correctly."""
        self.assertEqual(
            get_mapped_value("Nativa", ORIGIN_MAPPINGS), Species.Origin.NATIVE
        )

    def test_iucn_status_mappings(self):
        """Test that IUCN status mappings work correctly."""
        self.assertEqual(
            get_mapped_value("Vulnerable", IUCN_STATUS_MAPPINGS),
            Species.IUCNStatus.VULNERABLE,
        )

    def test_life_form_mappings(self):
        """Test that growth habit mappings work correctly."""
        self.assertEqual(
            get_mapped_value("Árbol", LIFEFORM_MAPPINGS), Species.LifeForm.TREE
        )

    def test_measured_attribute_mappings(self):
        """Test that measured attribute mappings work correctly."""
        self.assertEqual(
            get_mapped_value("Altura total", MEASURED_ATTRIBUTE_MAPPINGS),
            Measurement.MeasuredAttribute.TOTAL_HEIGHT,
        )

    def test_measurement_unit_mappings(self):
        """Test that measurement unit mappings work correctly."""
        self.assertEqual(
            get_mapped_value("m", MEASUREMENT_UNIT_MAPPINGS),
            Measurement.MeasurementUnit.METERS,
        )

    def test_reproductive_condition_mappings(self):
        """Test that reproductive condition mappings work correctly."""
        self.assertEqual(
            get_mapped_value("Floración", REPRODUCTIVE_CONDITION_MAPPINGS),
            Observation.ReproductiveCondition.FLOWERING,
        )

    def test_phytosanitary_status_mappings(self):
        """Test that phytosanitary status mappings work correctly."""
        self.assertEqual(
            get_mapped_value("Sano", PHYTOSANITARY_STATUS_MAPPINGS),
            Observation.PhytosanitaryStatus.HEALTHY,
        )
