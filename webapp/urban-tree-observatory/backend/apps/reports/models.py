import uuid

from django.contrib.auth.models import User
from django.contrib.gis.db import models
from django.utils.translation import gettext_lazy as _

from apps.trees.models import Tree


class Report(models.Model):
    """Citizen report for tree issues or observations"""

    uuid = models.UUIDField(_("UUID"), default=uuid.uuid4, editable=False)

    # User information
    reporter = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="tree_reports",
        verbose_name=_("Reporter"),
    )
    # For anonymous reporting
    reporter_name = models.CharField(_("Reporter Name"), max_length=100, blank=True)
    reporter_email = models.EmailField(_("Reporter Email"), blank=True)
    reporter_phone = models.CharField(_("Reporter Phone"), max_length=20, blank=True)

    # Tree information
    tree = models.ForeignKey(
        Tree,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reports",
        verbose_name=_("Tree"),
    )
    # If the tree is not in the database or the user doesn't know which tree
    location = models.PointField(
        _("Location"), srid=4326, geography=True, null=True, blank=True
    )
    address = models.CharField(_("Address"), max_length=255, blank=True)

    # Report details
    class ReportType(models.TextChoices):
        HAZARD = "hazard", _("Hazardous Condition")
        DAMAGE = "damage", _("Tree Damage")
        DISEASE = "disease", _("Disease or Pests")
        ILLEGAL_ACTIVITY = "illegal_activity", _("Illegal Activity")
        MAINTENANCE = "maintenance", _("Needs Maintenance")
        REQUEST = "request", _("Planting Request")
        REMOVAL = "removal", _("Removal Request")
        OBSERVATION = "observation", _("General Observation")
        OTHER = "other", _("Other")

    report_type = models.CharField(_("Report Type"), max_length=30, choices=ReportType)
    title = models.CharField(_("Title"), max_length=100)
    description = models.TextField(_("Description"))

    # Priority and status
    class PriorityLevel(models.TextChoices):
        LOW = "low", _("Low")
        MEDIUM = "medium", _("Medium")
        HIGH = "high", _("High")
        URGENT = "urgent", _("Urgent")

    priority = models.CharField(
        _("Priority"), max_length=10, choices=PriorityLevel, default="medium"
    )

    class ReportStatus(models.TextChoices):
        NEW = "new", _("New")
        UNDER_REVIEW = "under_review", _("Under Review")
        ASSIGNED = "assigned", _("Assigned")
        IN_PROGRESS = "in_progress", _("In Progress")
        RESOLVED = "resolved", _("Resolved")
        CLOSED = "closed", _("Closed")
        REJECTED = "rejected", _("Rejected")

    status = models.CharField(
        _("Status"), max_length=20, choices=ReportStatus, default="new"
    )

    # Timestamps
    created_at = models.DateTimeField(_("Reported At"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Updated At"), auto_now=True)
    closed_at = models.DateTimeField(_("Closed At"), null=True, blank=True)

    # Media attachments
    # Using separate model for multiple images

    # Admin fields
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_reports",
        verbose_name=_("Assigned To"),
    )
    admin_notes = models.TextField(_("Admin Notes"), blank=True)

    class Meta:
        verbose_name = _("Report")
        verbose_name_plural = _("Reports")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.get_report_type_display()} - {self.title}"


class ReportImage(models.Model):
    """Images attached to reports"""

    report = models.ForeignKey(
        Report,
        on_delete=models.CASCADE,
        related_name="images",
        verbose_name=_("Report"),
    )
    image = models.ImageField(_("Image"), upload_to="reports/%Y/%m/%d/")
    caption = models.CharField(_("Caption"), max_length=255, blank=True)
    uploaded_at = models.DateTimeField(_("Uploaded At"), auto_now_add=True)

    class Meta:
        verbose_name = _("Report Image")
        verbose_name_plural = _("Report Images")
        ordering = ["uploaded_at"]

    def __str__(self):
        return f"Image for {self.report}"


class Intervention(models.Model):
    """Interventions performed in response to reports"""

    uuid = models.UUIDField(_("UUID"), default=uuid.uuid4, editable=False)

    report = models.ForeignKey(
        Report,
        on_delete=models.CASCADE,
        related_name="interventions",
        verbose_name=_("Report"),
    )

    # Intervention details
    class InterventionType(models.TextChoices):
        INSPECTION = "inspection", _("Inspection")
        MAINTENANCE = "maintenance", _("Maintenance")
        PRUNING = "pruning", _("Pruning")
        TREATMENT = "treatment", _("Treatment")
        REMOVAL = "removal", _("Removal")
        PLANTING = "planting", _("Planting")
        OTHER = "other", _("Other")

    intervention_type = models.CharField(
        _("Intervention Type"), max_length=20, choices=InterventionType
    )

    # Actions taken
    performed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="performed_interventions",
        verbose_name=_("Performed By"),
    )
    date_performed = models.DateField(_("Date Performed"))
    description = models.TextField(_("Description"))
    cost = models.DecimalField(
        _("Cost"), max_digits=10, decimal_places=2, null=True, blank=True
    )

    # Outcome
    class ReportOutcome(models.TextChoices):
        SUCCESSFUL = "successful", _("Successful")
        PARTIAL = "partial", _("Partially Successful")
        UNSUCCESSFUL = "unsuccessful", _("Unsuccessful")
        NEEDS_FOLLOWUP = "needs_followup", _("Needs Follow-up")

    outcome = models.CharField(_("Outcome"), max_length=20, choices=ReportOutcome)
    followup_notes = models.TextField(_("Follow-up Notes"), blank=True)

    # Timestamps
    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Updated At"), auto_now=True)

    class Meta:
        verbose_name = _("Intervention")
        verbose_name_plural = _("Interventions")
        ordering = ["-date_performed"]

    def __str__(self):
        return f"{self.intervention_type} on {self.date_performed} for {self.report}"
