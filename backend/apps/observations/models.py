import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.trees.models import BiodiversityRecord


class Observation(models.Model):
    """
    Model to store observations of biodiversity records (trees).
    """

    class ReproductiveCondition(models.TextChoices):
        FLOWERING = "FL", _("flowering")
        FRUITING = "FR", _("fruiting")
        SEEDLING = "SE", _("seedling")
        VEGETATIVE = "VE", _("vegetative")
        NONE = "NO", _("none")

    class PhytosanitaryStatus(models.TextChoices):
        HEALTHY = "HE", _("healthy")
        INFECTED = "IN", _("infected")
        INFESTED = "IF", _("infested")
        NONE = "NO", _("none")

    class PhysicalCondition(models.TextChoices):
        GOOD = "GO", _("good")
        BAD = "BA", _("bad")
        REGULAR = "RE", _("regular")
        NONE = "NO", _("none")

    class FoliageDensity(models.TextChoices):
        DENSE = "DE", _("dense")
        MODERATE = "MO", _("moderate")
        SPARSE = "SP", _("sparse")
        NONE = "NO", _("none")

    class AestheticValue(models.TextChoices):
        DESIRABLE = "DE", _("desirable")
        EMBLEMATIC = "EM", _("emblematic")
        ESSENTIAL = "ES", _("essential")
        UNACCEPTABLE = "UN", _("unacceptable")
        INDIFFERENT = "IN", _("indifferent")
        NONE = "NO", _("none")

    class GrowthPhase(models.TextChoices):
        F1 = "F1", _("F1")
        F2 = "F2", _("F2")
        F3 = "F3", _("F3")
        UNKNOWN = "UN", _("unknown")

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
        SHRUB = "SH", _("shrub")
        HERB = "HE", _("herb")
        CLIMBER = "CL", _("climber")
        NONE = "NO", _("none")

    uuid = models.UUIDField(_("uuid"), default=uuid.uuid4, editable=False)
    biodiversity_record = models.ForeignKey(
        BiodiversityRecord,
        on_delete=models.CASCADE,
        related_name="observations",
        verbose_name=_("biodiversity record"),
    )
    comments = models.TextField(_("comments"), blank=True, default="No reportado")
    reproductive_condition = models.CharField(
        _("reproductive condition"),
        max_length=12,
        choices=ReproductiveCondition,
        default=ReproductiveCondition.NONE,
    )
    observations = models.TextField(
        _("observations"), blank=True, default="No reportado"
    )
    phytosanitary_status = models.CharField(
        _("phytosanitary status"),
        max_length=12,
        choices=PhytosanitaryStatus,
        default=PhytosanitaryStatus.NONE,
    )
    accompanying_collectors = models.TextField(
        _("accompanying collectors"), blank=True, default="No reportado"
    )
    use = models.URLField(_("use"), blank=True, null=True)
    physical_condition = models.CharField(
        _("physical condition"),
        max_length=12,
        choices=PhysicalCondition,
        default=PhysicalCondition.NONE,
    )
    foliage_density = models.CharField(
        _("foliage density"),
        max_length=12,
        choices=FoliageDensity,
        default=FoliageDensity.NONE,
    )
    aesthetic_value = models.CharField(
        _("aesthetic value"),
        max_length=12,
        choices=AestheticValue,
        default=AestheticValue.NONE,
    )
    growth_phase = models.CharField(
        _("growth phase"),
        max_length=12,
        choices=GrowthPhase,
        default=GrowthPhase.UNKNOWN,
    )
    origin = models.CharField(
        _("origin"),
        max_length=12,
        choices=Origin,
        default=Origin.UNKNOWN,
    )
    iucn_status = models.CharField(
        _("IUCN status"),
        max_length=24,
        choices=IUCNStatus,
        default=IUCNStatus.NOT_EVALUATED,
    )
    growth_habit = models.CharField(
        _("growth habit"),
        max_length=12,
        choices=GrowthHabit,
        default=GrowthHabit.NONE,
    )
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("updated at"), auto_now=True)
    date = models.DateField(_("observation date"), auto_now_add=True)
    recorded_by = models.CharField(
        _("recorded by"), max_length=255, default="Cortolima", blank=True
    )

    class Meta:
        verbose_name = _("observation")
        verbose_name_plural = _("observations")
        ordering = ["date"]

    def __str__(self):
        return f"{self.biodiversity_record} - {self.date}"
