from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.biodiversity.models import BiodiversityRecord
from apps.core.models import BaseModel


class Measurement(BaseModel):
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
        NOT_REPORTED = "NR", _("not reported")

    class MeasurementUnit(models.TextChoices):
        METERS = "m", _("meters")
        CUBIC_METERS = "m3", _("cubic meters")
        CENTIMETERS = "cm", _("centimeters")
        GRAMS_PER_CUBIC_CM = "g/cm3", _("grams per cubic centimeter")
        NOT_REPORTED = "NR", _("not reported")

    class MeasurementMethod(models.TextChoices):
        OPTICAL_ESTIMATION = "OE", _("optical estimation")
        VOLUME_EQUATION = "VE", _("volume equation")
        DIAMETER_TAPE = "DT", _("diameter tape")
        WOOD_DENSITY_DB = "WD", _("wood density database")
        NOT_REPORTED = "NR", _("not reported")

    biodiversity_record = models.ForeignKey(
        BiodiversityRecord,
        on_delete=models.CASCADE,
        related_name="measurements",
        verbose_name=_("biodiversity record"),
    )
    attribute = models.CharField(
        _("measured attribute"),
        max_length=3,
        choices=MeasuredAttribute,
        default=MeasuredAttribute.NOT_REPORTED,
    )
    value = models.FloatField(_("measurement value"))
    unit = models.CharField(
        _("measurement unit"),
        max_length=5,
        choices=MeasurementUnit,
        default=MeasurementUnit.NOT_REPORTED,
    )
    method = models.CharField(
        _("measurement method"),
        max_length=2,
        choices=MeasurementMethod,
        default=MeasurementMethod.NOT_REPORTED,
    )
    date = models.DateField(_("measurement date"), null=True, blank=True)

    class Meta:
        verbose_name = _("measurement")
        verbose_name_plural = _("measurements")
        ordering = ["-created_at"]

    def __str__(self):
        """Returns a string representation of the measurement, including the
        measured attribute, biodiversity record, and measurement date if available.
        Example: "trunk height measurement for biodiversity record #1 on 2025-10-01"
        """
        date_str = f" on {self.date}" if self.date else ""
        return (
            f"{self.get_attribute_display()} measurement for "
            f"biodiversity record #{self.biodiversity_record.id}{date_str}"
        )


class Observation(BaseModel):
    """Captures qualitative assessments of tree conditions and characteristics.

    Documents subjective evaluations including aesthetic value, health status,
    and reproductive phases that complement objective measurements."""

    class ReproductiveCondition(models.TextChoices):
        FLOWERING = "FL", _("flowering")
        FRUITING = "FR", _("fruiting")
        STERILE = "ST", _("sterile")
        NOT_REPORTED = "NR", _("not reported")

    class PhytosanitaryStatus(models.TextChoices):
        HEALTHY = "HE", _("healthy")
        SICK = "SI", _("sick")
        CRITICAL = "CR", _("critical")
        DEAD = "DE", _("dead")
        NOT_REPORTED = "NR", _("not reported")

    class PhysicalCondition(models.TextChoices):
        GOOD = "GO", _("good")
        FAIR = "FA", _("fair")
        POOR = "PO", _("poor")
        NOT_REPORTED = "NR", _("not reported")

    class FoliageDensity(models.TextChoices):
        DENSE = "DE", _("dense")
        MEDIUM = "ME", _("medium")
        SPARSE = "SP", _("sparse")
        NOT_REPORTED = "NR", _("not reported")

    class AestheticValue(models.TextChoices):
        ESSENTIAL = "ES", _("essential")
        EMBLEMATIC = "EM", _("emblematic")
        DESIRABLE = "DE", _("desirable")
        INDIFFERENT = "IN", _("indifferent")
        UNACCEPTABLE = "UN", _("unacceptable")
        NOT_REPORTED = "NR", _("not reported")

    class GrowthPhase(models.IntegerChoices):
        SEEDLING = 1, _("seedling")
        JUVENILE = 2, _("juvenile")
        ADULT = 3, _("adult")

    class YesNoReported(models.TextChoices):
        YES = "Y", _("yes")
        NO = "N", _("no")
        NOT_REPORTED = "NR", _("not reported")

    class HealthCondition(models.TextChoices):
        NATURAL_STATE = "NS", _("natural state")
        NUTRIENT_DEFICIENCY = "ND", _("nutrient deficiency")
        NOT_REPORTED = "NR", _("not reported")

    class DamagePercent(models.TextChoices):
        ZERO = "0", _("0%")
        TWENTY = "20", _("20%")
        FORTY = "40", _("40%")
        SIXTY = "60", _("60%")
        EIGHTY = "80", _("80%")
        HUNDRED = "100", _("100%")
        NOT_REPORTED = "NR", _("not reported")

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
    growth_phase = models.IntegerField(
        _("growth phase"),
        choices=GrowthPhase,
        default=GrowthPhase.SEEDLING,
    )

    # General status fields without explicit name in the original data
    ed = models.CharField(
        max_length=2,
        choices=PhysicalCondition,
        default=PhysicalCondition.NOT_REPORTED,
    )
    hc = models.CharField(
        max_length=2,
        choices=HealthCondition,
        default=HealthCondition.NOT_REPORTED,
    )
    hfc = models.CharField(
        max_length=2,
        choices=HealthCondition,
        default=HealthCondition.NOT_REPORTED,
    )

    # Maps to `general_state` text field in original data; converted to boolean
    is_standing = models.BooleanField(
        _("is standing"), default=True, help_text=_("Is the tree standing?")
    )

    # Yes/No/Not reported fields without explicit names in the original data
    cre = models.CharField(
        max_length=2,
        choices=YesNoReported,
        default=YesNoReported.NOT_REPORTED,
    )
    crh = models.CharField(
        max_length=2,
        choices=YesNoReported,
        default=YesNoReported.NOT_REPORTED,
    )
    cra = models.CharField(
        max_length=2,
        choices=YesNoReported,
        default=YesNoReported.NOT_REPORTED,
    )
    coa = models.CharField(
        max_length=2,
        choices=YesNoReported,
        default=YesNoReported.NOT_REPORTED,
    )
    ce = models.CharField(
        max_length=2,
        choices=YesNoReported,
        default=YesNoReported.NOT_REPORTED,
    )
    civ = models.CharField(
        max_length=2,
        choices=YesNoReported,
        default=YesNoReported.NOT_REPORTED,
    )
    crt = models.CharField(
        max_length=2,
        choices=YesNoReported,
        default=YesNoReported.NOT_REPORTED,
    )
    crg = models.CharField(
        max_length=2,
        choices=YesNoReported,
        default=YesNoReported.NOT_REPORTED,
    )
    cap = models.CharField(
        max_length=2,
        choices=YesNoReported,
        default=YesNoReported.NOT_REPORTED,
    )

    # Percentage damage fields without explicit names in the original data
    rd = models.CharField(
        max_length=3,
        choices=DamagePercent,
        default=DamagePercent.ZERO,
    )
    dm = models.CharField(
        max_length=3,
        choices=DamagePercent,
        default=DamagePercent.ZERO,
    )
    bbs = models.CharField(
        max_length=3,
        choices=DamagePercent,
        default=DamagePercent.ZERO,
    )
    ab = models.CharField(
        max_length=3,
        choices=DamagePercent,
        default=DamagePercent.ZERO,
    )
    pi = models.CharField(
        max_length=3,
        choices=DamagePercent,
        default=DamagePercent.ZERO,
    )
    ph = models.CharField(
        max_length=3,
        choices=DamagePercent,
        default=DamagePercent.ZERO,
    )
    pa = models.CharField(
        max_length=3,
        choices=DamagePercent,
        default=DamagePercent.ZERO,
    )
    pd = models.CharField(
        max_length=3,
        choices=DamagePercent,
        default=DamagePercent.ZERO,
    )
    pe = models.CharField(
        max_length=3,
        choices=DamagePercent,
        default=DamagePercent.ZERO,
    )
    pp = models.CharField(
        max_length=3,
        choices=DamagePercent,
        default=DamagePercent.ZERO,
    )
    po = models.CharField(
        max_length=3,
        choices=DamagePercent,
        default=DamagePercent.ZERO,
    )
    r_vol = models.CharField(
        max_length=3,
        choices=DamagePercent,
        default=DamagePercent.ZERO,
    )
    r_cr = models.CharField(
        max_length=3,
        choices=DamagePercent,
        default=DamagePercent.ZERO,
    )
    r_ce = models.CharField(
        max_length=3,
        choices=DamagePercent,
        default=DamagePercent.ZERO,
    )

    field_notes = models.TextField(_("field notes"), blank=True)
    recorded_by = models.CharField(_("recorded by"), max_length=50, default="Cortolima")
    accompanying_collectors = models.TextField(_("accompanying collectors"), blank=True)
    date = models.DateField(_("observation date"), null=True, blank=True)

    class Meta:
        verbose_name = _("observation")
        verbose_name_plural = _("observations")
        ordering = ["-created_at"]

    def __str__(self):
        date_str = f" on {self.date}" if self.date else ""
        return f"Observation for {self.biodiversity_record}{date_str}"
