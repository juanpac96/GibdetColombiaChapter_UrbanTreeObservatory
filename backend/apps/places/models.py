from django.db import models

from apps.core.models import BaseModel

from django.utils.translation import gettext_lazy as _


class Country(models.Model):
    """Represents a country."""

    name = models.CharField(
        _("country"), max_length=50, default="Colombia", unique=True
    )

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Department(models.Model):
    """Represents a department within a country."""

    name = models.CharField(
        _("department"), max_length=50, default="Tolima", unique=True
    )
    country = models.ForeignKey(
        Country,
        on_delete=models.CASCADE,
        related_name="departments",
        verbose_name=_("country"),
    )

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name}, {self.country.name}"


class Municipality(models.Model):
    """Represents a municipality within a department."""

    name = models.CharField(
        _("municipality"), max_length=50, default="Ibagué", unique=True
    )
    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name="municipalities",
        verbose_name=_("department"),
    )

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name}, {self.department.name}"


class Place(BaseModel):
    """Represents a general geographical location of biodiversity records."""

    country = models.ForeignKey(
        Country,
        on_delete=models.CASCADE,
        related_name="places",
        verbose_name=_("country"),
    )
    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name="places",
        verbose_name=_("department"),
    )
    municipality = models.ForeignKey(
        Municipality,
        on_delete=models.CASCADE,
        related_name="places",
        verbose_name=_("municipality"),
    )
    site = models.CharField(_("site"), max_length=50)
    populated_center = models.CharField(_("populated center"), max_length=50)
    zone = models.PositiveSmallIntegerField(_("zone"), null=True, blank=True)
    subzone = models.PositiveSmallIntegerField(_("subzone"), null=True, blank=True)

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
