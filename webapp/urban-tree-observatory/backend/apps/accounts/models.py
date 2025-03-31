from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    bio = models.TextField(_("bio"), max_length=500, blank=True)
    phone_number = models.CharField(_("phone number"), max_length=20, blank=True)
    organization = models.CharField(_("organization"), max_length=100, blank=True)

    class Meta:
        verbose_name = _("user profile")
        verbose_name_plural = _("user profiles")

    def __str__(self):
        return self.user


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.userprofile.save()


class Role(models.Model):
    class RoleType(models.TextChoices):
        REPORTER = "RP", _("Reporter")
        TREE_MANAGER = "TM", _("Tree Manager")
        ANALYST = "AN", _("Analyst")

    type = models.CharField(
        max_length=100, unique=True, choices=RoleType, default=RoleType.REPORTER
    )
    description = models.TextField(blank=True)

    def __str__(self):
        return self.type


class UserRole(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_roles")
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    area_of_responsibility = models.CharField(
        _("area of responsibility"), max_length=100, blank=True
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "role"], name="unique_user_role")
        ]
