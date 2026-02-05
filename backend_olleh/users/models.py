import uuid

from django.db import models

from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.translation import gettext_lazy as _


class CustomUserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError(_("The Email must be set"))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("Superuser must have is_staff=True."))
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("Superuser must have is_superuser=True."))

        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    username = None
    email = models.EmailField(_("email address"), unique=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
    EMAIL_FIELD = "email"

    objects = CustomUserManager()

    def __str__(self):
        return self.email


# ---------- Reputation (OLLEH agreement) ----------
class MemberProfile(models.Model):
    """
    OLLEH member profile: unique OLLEH code, reputation, and agreement details.
    """

    REPUTATION_STARTER = "starter"
    REPUTATION_TRUSTED = "trusted"
    REPUTATION_ELITE = "elite"

    REPUTATION_CHOICES = [
        (REPUTATION_STARTER, "Starter"),
        (REPUTATION_TRUSTED, "Trusted"),
        (REPUTATION_ELITE, "Elite"),
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="member_profile",
    )
    olleh_code = models.CharField(
        max_length=20,
        unique=True,
        blank=True,
        help_text="Unique OLLEH member ID/code (auto-generated if empty)",
    )
    reputation = models.CharField(
        max_length=20,
        choices=REPUTATION_CHOICES,
        default=REPUTATION_STARTER,
    )
    phone = models.CharField(max_length=20, blank=True)
    national_id = models.CharField(max_length=50, blank=True)
    full_name = models.CharField(max_length=150, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Member profile"
        verbose_name_plural = "Member profiles"

    def __str__(self):
        return f"{self.olleh_code or 'N/A'} – {self.user.email}"

    def save(self, *args, **kwargs):
        if not self.olleh_code:
            self.olleh_code = f"OLLEH-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)


class MemberMeasurements(models.Model):
    """
    Optional body and shoe measurements for fit assistance.
    OLLEH is not responsible for fit once item is approved by member.
    """

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="measurements",
    )
    height_cm = models.PositiveSmallIntegerField(null=True, blank=True)
    chest_cm = models.PositiveSmallIntegerField(null=True, blank=True)
    waist_cm = models.PositiveSmallIntegerField(null=True, blank=True)
    hip_cm = models.PositiveSmallIntegerField(null=True, blank=True)
    shoe_size_eu = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        null=True,
        blank=True,
    )
    notes = models.CharField(max_length=200, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Member measurements"
        verbose_name_plural = "Member measurements"

    def __str__(self):
        return f"Measurements – {self.user.email}"
