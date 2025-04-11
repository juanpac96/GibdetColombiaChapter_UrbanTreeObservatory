import uuid

from django.contrib.gis.db import models as gis_models
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.taxonomy.models import Species


class Place(models.Model):
    """Represents a general geographical location of biodiversity records."""

    uuid = models.UUIDField(_("uuid"), default=uuid.uuid4, editable=False)
    country = models.CharField(_("country"), default="Colombia", max_length=50)
    department = models.CharField(_("department"), default="Tolima", max_length=50)
    municipality = models.CharField(_("municipality"), default="Ibagué", max_length=50)
    site = models.CharField(_("site"), max_length=50, blank=True)
    populated_center = models.CharField(
        _("populated center"), max_length=50, blank=True
    )
    zone = models.PositiveSmallIntegerField(_("zone"), null=True, blank=True)
    subzone = models.PositiveSmallIntegerField(_("subzone"), null=True, blank=True)
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("updated at"), auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["country", "department", "municipality", "site"],
                name="unique_place",
            )
        ]
        ordering = ["country", "department", "municipality", "site"]

    def __str__(self):
        """Returns a string representation of the place, including the site,
        municipality, department, and country, if they are not empty.

        Example: "Parque Centenario, Ibagué, Tolima, Colombia"
        """
        components = [self.site, self.municipality, self.department, self.country]
        return ", ".join(filter(None, components))


class BiodiversityRecord(models.Model):
    """Represents a record of biodiversity, including species, location,
    common names, and other attributes."""

    uuid = models.UUIDField(_("uuid"), default=uuid.uuid4, editable=False)
    species = models.ForeignKey(
        Species,
        on_delete=models.PROTECT,
        related_name="biodeversity_records",
        verbose_name=_("species"),
    )
    place = models.ForeignKey(
        Place,
        on_delete=models.PROTECT,
        related_name="biodiversity_records",
        verbose_name=_("place"),
    )
    common_names = models.TextField(_("common names"), blank=True)
    location = gis_models.PointField(_("location"), srid=4326, geography=True)
    elevation_m = models.FloatField(_("elevation (m)"), null=True, blank=True)
    recorded_by = models.CharField(
        _("recorded by"), max_length=50, default="Cortolima", blank=True
    )
    date = models.DateField(_("recorded date"), null=True, blank=True)
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("updated at"), auto_now=True)

    class Meta:
        verbose_name = _("biodiversity record")
        verbose_name_plural = _("biodiversity records")
        ordering = ["species", "location"]

    def __str__(self):
        return f"{self.species.scientific_name} at {self.longitude}, {self.latitude}"

    @property
    def longitude(self):
        """Get the longitude of the biodiversity record's location"""
        return self.location.x if self.location else None

    @property
    def latitude(self):
        """Get the latitude of the biodiversity record's location"""
        return self.location.y if self.location else None
