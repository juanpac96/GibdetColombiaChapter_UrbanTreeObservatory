import uuid

from django.db import models
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


class Trait(models.Model):
    """Represents a trait that can be measured for a species group."""

    class TraitType(models.TextChoices):
        CARBON_SEQUESTRATION_IDX = "CARBON", _("carbon sequestration index")
        SHADE_IDX = "SHADE", _("shade index")
        CANOPY_DIAMETER_MAX = "CANOPY", _("maximum diameter of canopy (m)")
        TOTAL_HEIGHT_MAX = "HEIGHT", _("maximum total height (m)")
    
    uuid = models.UUIDField(_("uuid"), default=uuid.uuid4, editable=False)
    type = models.CharField(
        _("trait type"),
        max_length=6,
        choices=TraitType,
    )
    
    class Meta:
        verbose_name = _("trait")
        verbose_name_plural = _("traits")
        ordering = ["type"]
        
    def __str__(self):
        return self.get_type_display()


class TraitValue(models.Model):
    """Represents a specific trait value range for a functional group."""
    
    uuid = models.UUIDField(_("uuid"), default=uuid.uuid4, editable=False)
    trait = models.ForeignKey(
        Trait,
        on_delete=models.CASCADE,
        related_name="trait_values",
        verbose_name=_("trait"),
    )
    functional_group = models.ForeignKey(
        "FunctionalGroup",
        on_delete=models.CASCADE,
        related_name="trait_values",
        verbose_name=_("functional group"),
    )
    min_value = models.FloatField(
        _("minimum value"),
        help_text=_("minimum value for this trait in the functional group"),
    )
    max_value = models.FloatField(
        _("maximum value"),
        help_text=_("maximum value for this trait in the functional group"),
    )

    class Meta:
        verbose_name = _("trait value")
        verbose_name_plural = _("trait values")
        constraints = [
            models.UniqueConstraint(
                fields=["trait", "functional_group"],
                name="unique_trait_functional_group",
            ),
            models.CheckConstraint(
                check=models.Q(min_value__lte=models.F("max_value")),
                name="min_value_less_than_max_value",
            ),
            models.CheckConstraint(
                check=models.Q(min_value__gte=0),
                name="min_value_greater_than_zero",
            ),
            models.CheckConstraint(
                check=models.Q(max_value__gte=0),
                name="max_value_greater_than_zero",
            ),
        ]

    def __str__(self):
        return f"{self.trait}: {self.min_value}-{self.max_value}"


class FunctionalGroup(models.Model):
    """Represents a functional group of species."""

    uuid = models.UUIDField(_("uuid"), default=uuid.uuid4, editable=False)
    group_id = models.PositiveSmallIntegerField(
        _("group id"),
        help_text=_("unique identifier for the functional group"),
        unique=True,
    )
    description = models.TextField(
        _("description"),
        help_text=_("description of the functional group"),
        blank=True,
    )
    traits = models.ManyToManyField(
        Trait,
        through="TraitValue",
        related_name="functional_groups",
        verbose_name=_("traits"),
    )

    class Meta:
        verbose_name = _("functional group")
        verbose_name_plural = _("functional groups")
        ordering = ["id"]

    def __str__(self):
        return f"Group {str(self.group_id)}"


class Species(models.Model):
    """Represents a species, including its genus and family."""

    class Origin(models.TextChoices):
        EXOTIC = "EX", _("exotic")
        NATIVE = "NA", _("native")
        ENDEMIC = "EN", _("endemic")
        NOT_IDENTIFIED = "NI", _("not identified")

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

    class LifeForm(models.TextChoices):
        TREE = "TR", _("tree")
        PALM_TREE = "PT", _("palm tree")
        SHRUB = "SH", _("shrub")
        OTHER = "OT", _("other")

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
    functional_group = models.ForeignKey(
        FunctionalGroup,
        on_delete=models.SET_NULL,
        related_name="species",
        verbose_name=_("functional group"),
        null=True,
    )
    accepted_scientific_name = models.CharField(
        _("accepted scientific name"),
        max_length=150,
        help_text=_(
            "scientific genus and species name with optional reference to whom named it"
        ),
        default="No identificado",
    )
    origin = models.CharField(
        _("origin"),
        max_length=2,
        choices=Origin,
        default=Origin.NOT_IDENTIFIED,
    )
    iucn_status = models.CharField(
        _("IUCN status"),
        max_length=2,
        choices=IUCNStatus,
        default=IUCNStatus.NOT_EVALUATED,
    )
    life_form = models.CharField(
        _("life form"),
        max_length=2,
        choices=LifeForm,
        default=LifeForm.TREE,
    )
    gbif_id = models.CharField(
        _("GBIF ID"),
        max_length=20, 
        blank=True, 
        help_text="GBIF species identifier"
    )
    use = models.CharField(
        _("use"),
        max_length=255,
        default="No reportado",
        help_text=_("common local use of the species"),
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
        ordering = ["genus", "name"]
        constraints = [
            models.UniqueConstraint(
                fields=["genus", "name"],
                name="unique_genus_species",
            ),
        ]

    def __str__(self):
        return self.scientific_name

    @property
    def gbif_url(self):
        if self.gbif_id and self.gbif_id != "No identificado":
            return f"https://www.gbif.org/species/{self.gbif_id}"
        return None

    @property
    def scientific_name(self):
        """Return the scientific name of the species."""
        return f"{self.genus} {self.name}"
