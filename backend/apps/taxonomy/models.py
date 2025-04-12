import uuid

from django.db import models
from django.db.models.functions import Concat
from django.utils.translation import gettext_lazy as _


class Family(models.Model):
    uuid = models.UUIDField(_("uuid"), default=uuid.uuid4, editable=False)
    name = models.CharField(_("family name"), max_length=50, unique=True)

    class Meta:
        verbose_name = _("family")
        verbose_name_plural = _("families")
        ordering = ["name"]

    def __str__(self):
        return self.name


class Genus(models.Model):
    uuid = models.UUIDField(_("uuid"), default=uuid.uuid4, editable=False)
    name = models.CharField(_("genus name"), max_length=50, unique=True)
    family = models.ForeignKey(
        Family,
        on_delete=models.CASCADE,
        related_name="genera",
        verbose_name=_("family"),
    )

    class Meta:
        verbose_name = _("genus")
        verbose_name_plural = _("genera")
        ordering = ["name"]

    def __str__(self):
        return self.name


class Species(models.Model):
    """Represents a species, including its genus and family."""

    class Origin(models.TextChoices):
        EXOTIC = "EX", _("exotic")
        NATIVE = "NA", _("native")
        UNKNOWN = "UN", _("unknown")

    class IUCNStatus(models.TextChoices):
        DATA_DEFICIENT = "DD", _("data deficient")
        LEAST_CONCERN = "LC", _("least concern")
        NEAR_THREATENED = "NT", _("near threatened")
        VULNERABLE = "VU", _("vulnerable")
        ENDANGERED = "EN", _("endangered")
        CRITICALLY_ENDANGERED = "CR", _("critically endangered")
        EXTINCT_IN_WILD = "EW", _("extinct in the wild")
        EXTINCT = "EX", _("extinct")
        NOT_EVALUATED = "NE", _("not evaluated")

    class GrowthHabit(models.TextChoices):
        TREE = "TR", _("tree")
        PALM_TREE = "PT", _("palm tree")
        SHRUB = "SH", _("shrub")
        UNKNOWN = "UN", _("unknown")

    uuid = models.UUIDField(_("uuid"), default=uuid.uuid4, editable=False)
    genus = models.ForeignKey(
        Genus,
        on_delete=models.CASCADE,
        related_name="species",
        verbose_name=_("genus"),
    )
    name = models.CharField(
        _("species name"), max_length=50, help_text=_("species name without the genus")
    )
    scientific_name = models.GeneratedField(
        expression=Concat(
            "genus",
            models.Value(" "),
            "name",
        ),
        output_field=models.CharField(max_length=101),
        db_persist=True,
        verbose_name=_("scientific genus and species name"),
    )
    accepted_scientific_name = models.CharField(
        _("accepted scientific name"),
        max_length=50,
        unique=True,
        help_text=_(
            "scientific genus and species name with optional reference to whom named it"
        ),
    )
    origin = models.CharField(
        _("origin"),
        max_length=2,
        choices=Origin,
        default=Origin.UNKNOWN,
    )
    iucn_status = models.CharField(
        _("IUCN status"),
        max_length=2,
        choices=IUCNStatus,
        default=IUCNStatus.NOT_EVALUATED,
    )
    growth_habit = models.CharField(
        _("growth habit"),
        max_length=2,
        choices=GrowthHabit,
        default=GrowthHabit.UNKNOWN,
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
        ordering = ["scientific_name"]

    def __str__(self):
        return self.scientific_name
