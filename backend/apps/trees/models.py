import uuid

from django.contrib.gis.db import models
from django.utils.translation import gettext_lazy as _


class Family(models.Model):
    uuid = models.UUIDField(_("uuid"), default=uuid.uuid4, editable=False)
    name = models.CharField(_("family name"), max_length=255, unique=True)

    class Meta:
        verbose_name = _("family")
        verbose_name_plural = _("families")

    def __str__(self):
        return self.name


class Genus(models.Model):
    uuid = models.UUIDField(_("uuid"), default=uuid.uuid4, editable=False)
    name = models.CharField(_("genus name"), max_length=255, unique=True)
    family = models.ForeignKey(
        Family,
        on_delete=models.CASCADE,
        related_name="genera",
        verbose_name=_("family"),
    )

    class Meta:
        verbose_name = _("genus")
        verbose_name_plural = _("genera")

    def __str__(self):
        return self.name


class Species(models.Model):
    uuid = models.UUIDField(_("uuid"), default=uuid.uuid4, editable=False)
    name = models.CharField(_("species name"), max_length=255)
    accepted_scientific_name = models.CharField(
        _("accepted scientific name"), max_length=255, unique=True
    )
    genus = models.ForeignKey(
        Genus,
        on_delete=models.CASCADE,
        related_name="species",
        verbose_name=_("genus"),
    )
    identified_by = models.CharField(
        _("identified by"), max_length=255, default="Cortolima", blank=True
    )
    identified_date = models.DateField(_("identified date"), null=True, blank=True)
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("updated at"), auto_now=True)

    class Meta:
        verbose_name = _("species")
        verbose_name_plural = _("species")
        ordering = ["accepted_scientific_name"]

    def __str__(self):
        return self.accepted_scientific_name


class Place(models.Model):
    uuid = models.UUIDField(_("uuid"), default=uuid.uuid4, editable=False)
    country = models.CharField(_("country"), default="Colombia", max_length=255)
    department = models.CharField(_("department"), default="Tolima", max_length=255)
    municipality = models.CharField(_("municipality"), default="Ibagué", max_length=255)
    populated_center = models.CharField(
        _("populated center"), max_length=255, blank=True
    )
    zone = models.CharField(_("zone"), max_length=255, blank=True)
    subzone = models.CharField(_("subzone"), max_length=255, blank=True)
    site = models.CharField(_("site"), max_length=255, blank=True)
    created_by = models.CharField(_("created by"), max_length=255, blank=True)
    updated_by = models.CharField(_("updated by"), max_length=255, blank=True)
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("updated at"), auto_now=True)

    class Meta:
        verbose_name = _("place")
        verbose_name_plural = _("places")
        constraints = [
            models.UniqueConstraint(
                fields=["country", "department", "municipality", "site"],
                name="unique_place",
            )
        ]

    def __str__(self):
        return self.site


class BiodiversityRecord(models.Model):
    """Individual tree instance with geospatial data"""

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
    location = models.PointField(_("location"), srid=4326, geography=True)
    elevation_m = models.FloatField(_("elevation (m)"), null=True, blank=True)
    registered_by = models.CharField(
        _("registered by"), max_length=255, default="Cortolima", blank=True
    )
    registered_date = models.DateField(_("registered date"), null=True, blank=True)
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("updated at"), auto_now=True)

    class Meta:
        verbose_name = _("biodiversity record")
        verbose_name_plural = _("biodiversity records")
        ordering = ["species", "location"]

    def __str__(self):
        return f"{self.species.accepted_scientific_name} at {self.longitude}, {self.latitude}"

    @property
    def longitude(self):
        """Get the longitude of the tree's location"""
        return self.location.x if self.location else None

    @property
    def latitude(self):
        """Get the latitude of the tree's location"""
        return self.location.y if self.location else None


class Measurement(models.Model):
    """A measurement of a tree instance"""

    uuid = models.UUIDField(_("uuid"), default=uuid.uuid4, editable=False)
    biodiversity_record = models.ForeignKey(
        BiodiversityRecord,
        on_delete=models.CASCADE,
        related_name="measurements",
        verbose_name=_("biodiversity record"),
    )
    name = models.CharField(_("measurement name"), max_length=255)
    value = models.FloatField(_("measurement value"))
    method = models.CharField(_("measurement method"), max_length=255, blank=True)
    date = models.DateField(_("measurement date"), null=True, blank=True)
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("updated at"), auto_now=True)

    class Meta:
        verbose_name = _("measurement")
        verbose_name_plural = _("measurements")
        ordering = ["biodiversity_record", "created_at"]

    def __str__(self):
        return f"Measurement for {self.biodiversity_record}"
