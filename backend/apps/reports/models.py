import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.biodiversity.models import BiodiversityRecord


class Measurement(models.Model):
    """Records quantifiable attributes like trunk height or total height for trees.

    Stores numeric data collected through defined methodologies with
    tracking of measurement dates and techniques."""

    class MeasuredAttribute(models.TextChoices):
        TRUNK_HEIGHT = "TH", _("trunk height")
        TOTAL_HEIGHT = "HT", _("total height")
        CROWN_DIAMETER = "CD", _("crown diameter")
        DIAMETER_BH = "DBH", _("diameter at breast height")
        VOLUME = "VO", _("volume")
        WOOD_DENSITY = "WD", _("wood density")
        OTHER = "OT", _("other")
        NOT_REPORTED = "NO", _("not reported")

    class MeasurementUnit(models.TextChoices):
        METERS = "m", _("meters")
        CUBIC_METERS = "m3", _("cubic meters")
        CENTIMETERS = "cm", _("centimeters")
        MILLIMETERS = "mm", _("millimeters")
        GRAMS_PER_CUBIC_CM = "g/cm3", _("grams per cubic centimeter")
        OTHER = "OT", _("other")
        NOT_REPORTED = "NO", _("not reported")

    class MeasurementMethod(models.TextChoices):
        OPTICAL_ESTIMATION = "OE", _("optical estimation")
        VOLUME_EQUATION = "VE", _("volume equation")
        DIAMETER_TAPE = "DT", _("diameter tape")
        WOOD_DENSITY_DB = "WD", _("wood density database")
        OTHER = "OT", _("other")
        NOT_REPORTED = "NO", _("not reported")

    uuid = models.UUIDField(_("uuid"), default=uuid.uuid4, editable=False)
    biodiversity_record = models.ForeignKey(
        BiodiversityRecord,
        on_delete=models.CASCADE,
        related_name="measurements",
        verbose_name=_("biodiversity record"),
    )
    attribute = models.CharField(
        _("measured attribute"), max_length=3, choices=MeasuredAttribute
    )
    other_attribute = models.CharField(
        _("other attribute specification"), max_length=50, blank=True
    )
    value = models.FloatField(_("measurement value"))
    unit = models.CharField(
        _("measurement unit"), max_length=5, choices=MeasurementUnit
    )
    other_unit = models.CharField(
        _("other unit specification"), max_length=20, blank=True
    )
    method = models.CharField(
        _("measurement method"), max_length=2, choices=MeasurementMethod
    )
    other_method = models.CharField(
        _("other method specification"), max_length=50, blank=True
    )
    notes = models.TextField(_("notes"), blank=True)
    date = models.DateField(_("measurement date"), null=True, blank=True)
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("updated at"), auto_now=True)

    class Meta:
        verbose_name = _("measurement")
        verbose_name_plural = _("measurements")
        ordering = ["biodiversity_record", "created_at"]

    def __str__(self):
        date_str = f" on {self.date}" if self.date else ""
        return f"{self.get_attribute_display()} measurement for {self.biodiversity_record}{date_str}"


class Observation(models.Model):
    """Captures qualitative assessments of tree conditions and characteristics.

    Documents subjective evaluations including aesthetic value, health status,
    and reproductive phases that complement objective measurements."""

    class ReproductiveCondition(models.TextChoices):
        FLOWERING = "FL", _("flowering")
        FRUITING = "FR", _("fruiting")
        STERILE = "ST", _("sterile")
        NOT_REPORTED = "NO", _("not reported")

    class PhytosanitaryStatus(models.TextChoices):
        HEALTHY = "HE", _("healthy")
        SICK = "SI", _("sick")
        CRITICALLY_SICK = "CR", _("critically sick")
        DEAD = "DE", _("dead")
        NOT_REPORTED = "NO", _("not reported")

    class PhysicalCondition(models.TextChoices):
        GOOD = "GO", _("good")
        FAIR = "FA", _("fair")
        POOR = "PO", _("poor")
        NOT_REPORTED = "NO", _("not reported")

    class FoliageDensity(models.TextChoices):
        DENSE = "DE", _("dense")
        MEDIUM = "ME", _("medium")
        SPARSE = "SP", _("sparse")
        NOT_REPORTED = "NO", _("not reported")

    class AestheticValue(models.TextChoices):
        ESSENTIAL = "ES", _("essential")
        EMBLEMATIC = "EM", _("emblematic")
        DESIRABLE = "DE", _("desirable")
        INDIFFERENT = "IN", _("indifferent")
        UNACCEPTABLE = "UN", _("unacceptable")
        NOT_REPORTED = "NO", _("not reported")

    class GrowthPhase(models.TextChoices):
        F1 = "F1", _("F1")
        F2 = "F2", _("F2")
        F3 = "F3", _("F3")
        NOT_REPORTED = "NO", _("not reported")

    uuid = models.UUIDField(_("uuid"), default=uuid.uuid4, editable=False)
    biodiversity_record = models.ForeignKey(
        BiodiversityRecord,
        on_delete=models.CASCADE,
        related_name="observations",
        verbose_name=_("biodiversity record"),
    )
    reproductive_condition = models.CharField(
        _("reproductive condition"),
        max_length=2,
        choices=ReproductiveCondition,
        default=ReproductiveCondition.NOT_REPORTED,
    )
    phytosanitary_status = models.CharField(
        _("phytosanitary status"),
        max_length=2,
        choices=PhytosanitaryStatus,
        default=PhytosanitaryStatus.NOT_REPORTED,
    )
    physical_condition = models.CharField(
        _("physical condition"),
        max_length=2,
        choices=PhysicalCondition,
        default=PhysicalCondition.NOT_REPORTED,
    )
    foliage_density = models.CharField(
        _("foliage density"),
        max_length=2,
        choices=FoliageDensity,
        default=FoliageDensity.NOT_REPORTED,
    )
    aesthetic_value = models.CharField(
        _("aesthetic value"),
        max_length=2,
        choices=AestheticValue,
        default=AestheticValue.NOT_REPORTED,
    )
    growth_phase = models.CharField(
        _("growth phase"),
        max_length=2,
        choices=GrowthPhase,
        default=GrowthPhase.NOT_REPORTED,
    )
    notes = models.TextField(_("notes"), blank=True)
    recorded_by = models.CharField(
        _("recorded by"), max_length=50, default="Cortolima", blank=True
    )
    accompanying_collectors = models.TextField(
        _("accompanying collectors"), blank=True, default="No reportado"
    )
    date = models.DateField(_("observation date"), null=True, blank=True)
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("updated at"), auto_now=True)

    class Meta:
        verbose_name = _("observation")
        verbose_name_plural = _("observations")
        ordering = ["biodiversity_record", "created_at"]

    def __str__(self):
        date_str = f" on {self.date}" if self.date else ""
        return f"Observation for {self.biodiversity_record}{date_str}"
