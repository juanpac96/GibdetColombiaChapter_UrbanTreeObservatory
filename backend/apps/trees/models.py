import uuid

from django.contrib.gis.db import models
from django.utils.translation import gettext_lazy as _


class Species(models.Model):
    """Tree species classification"""

    uuid = models.UUIDField(_("UUID"), default=uuid.uuid4, editable=False)
    scientific_name = models.CharField(_("Scientific Name"), max_length=255)
    common_name = models.CharField(_("Common Name"), max_length=255)
    family = models.CharField(_("Family"), max_length=255, blank=True)
    native = models.BooleanField(_("Native Species"), default=False)
    description = models.TextField(_("Description"), blank=True)

    # Growth characteristics
    average_height = models.FloatField(_("Average Height (m)"), null=True, blank=True)
    average_canopy_diameter = models.FloatField(
        _("Average Canopy Diameter (m)"), null=True, blank=True
    )
    growth_rate = models.CharField(
        _("Growth Rate"),
        max_length=10,
        choices=[("slow", "Slow"), ("medium", "Medium"), ("fast", "Fast")],
        blank=True,
    )

    # Environmental benefits
    carbon_sequestration = models.FloatField(
        _("Carbon Sequestration (kg/year)"), null=True, blank=True
    )
    oxygen_production = models.FloatField(
        _("Oxygen Production (kg/year)"), null=True, blank=True
    )

    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Updated At"), auto_now=True)

    class Meta:
        verbose_name = _("Species")
        verbose_name_plural = _("Species")
        ordering = ["scientific_name"]

    def __str__(self):
        return f"{self.scientific_name} ({self.common_name})"


class Tree(models.Model):
    """Individual tree instance with geospatial data"""

    uuid = models.UUIDField(_("UUID"), default=uuid.uuid4, editable=False)

    # Tree identification
    species = models.ForeignKey(
        Species,
        on_delete=models.PROTECT,
        related_name="trees",
        verbose_name=_("Species"),
    )

    # Location data (using GeoDjango)
    location = models.PointField(_("Location"), srid=4326, geography=True)
    address = models.CharField(_("Address"), max_length=255, blank=True)
    neighborhood = models.CharField(_("Neighborhood"), max_length=100, blank=True)

    # Tree characteristics
    height = models.FloatField(_("Height (m)"), null=True, blank=True)
    trunk_diameter = models.FloatField(_("Trunk Diameter (cm)"), null=True, blank=True)
    canopy_diameter = models.FloatField(_("Canopy Diameter (m)"), null=True, blank=True)
    estimated_age = models.PositiveIntegerField(
        _("Estimated Age (years)"), null=True, blank=True
    )
    planting_date = models.DateField(_("Planting Date"), null=True, blank=True)

    # Health and status
    class HealthStatus(models.TextChoices):
        EXCELLENT = "excellent", _("Excellent")
        GOOD = "good", _("Good")
        FAIR = "fair", _("Fair")
        POOR = "poor", _("Poor")
        CRITICAL = "critical", _("Critical")
        DEAD = "dead", _("Dead")

    health_status = models.CharField(
        _("Health Status"),
        max_length=20,
        choices=HealthStatus,
        default=HealthStatus.GOOD,
    )
    health_notes = models.TextField(_("Health Notes"), blank=True)

    # Metadata
    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Updated At"), auto_now=True)
    last_inspection_date = models.DateField(
        _("Last Inspection Date"), null=True, blank=True
    )

    class Meta:
        ordering = ["species", "location"]

    def __str__(self):
        return f"{self.species.common_name} at {self.adress}"

    @property
    def is_native(self):
        """Check if the tree is a native species"""
        return self.species.native

    @property
    def carbon_benefit(self):
        """Calculate carbon sequestration benefit based on the tree's characteristics"""
        # Simplified calculation based on species average and tree size
        if self.species.carbon_sequestration and self.trunk_diameter:
            return (self.trunk_diameter / 30) * self.species.carbon_sequestration
        return None


class Maintenance(models.Model):
    """Record of maintenance activities performed on trees"""

    uuid = models.UUIDField(_("UUID"), default=uuid.uuid4, editable=False)

    tree = models.ForeignKey(
        Tree,
        on_delete=models.CASCADE,
        related_name="maintenance_records",
        verbose_name=_("Tree"),
    )

    class MaintenanceType(models.TextChoices):
        PRUNING = "pruning", _("Pruning")
        FERTILIZATION = "fertilization", _("Fertilization")
        PEST_CONTROL = "pest_control", _("Pest Control")
        DISEASE_TREATMENT = "disease_treatment", _("Disease Treatment")
        WATERING = "watering", _("Watering")
        STAKING = "staking", _("Staking")
        MULCHING = "mulching", _("Mulching")
        REMOVAL = "removal", _("Removal")
        PLANTING = "planting", _("Planting")
        INSPECTION = "inspection", _("Inspection")
        OTHER = "other", _("Other")

    maintenance_type = models.CharField(
        _("Maintenance Type"), max_length=30, choices=MaintenanceType
    )
    date_performed = models.DateField(_("Date Performed"))
    performed_by = models.CharField(_("Performed By"), max_length=255)
    description = models.TextField(_("Description"))
    cost = models.DecimalField(
        _("Cost"), max_digits=10, decimal_places=2, null=True, blank=True
    )

    # Before and after assessment
    before_health = models.CharField(
        _("Health Before"), max_length=20, choices=Tree.HealthStatus, blank=True
    )
    after_health = models.CharField(
        _("Health After"), max_length=20, choices=Tree.HealthStatus, blank=True
    )

    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Updated At"), auto_now=True)

    class Meta:
        verbose_name = _("Maintenance Record")
        verbose_name_plural = _("Maintenance Records")
        ordering = ["-date_performed"]

    def __str__(self):
        return f"{self.maintenance_type} for {self.tree} on {self.date_performed}"
