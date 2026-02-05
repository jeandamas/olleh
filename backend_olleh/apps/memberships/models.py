from datetime import timedelta

from django.db import models, transaction
from django.db.models import Q
from django.utils import timezone
from django.core.exceptions import ValidationError

from apps.common.models import BaseModel
from users.models import User


# =========================
# Membership Tier
# =========================

# Default duration: 1 year (per OLLEH agreement)
DEFAULT_MEMBERSHIP_DURATION_DAYS = 365


class Membership(BaseModel):
    """
    Membership tier (Basic, Premium). Fee is annual; duration is 1 year from activation.
    """

    name = models.CharField(max_length=50, unique=True)
    price = models.PositiveIntegerField(
        help_text="Annual membership fee in RWF (Rwandan Francs)"
    )
    max_order_price = models.PositiveIntegerField(
        help_text="Maximum layaway/order value in RWF for this tier"
    )
    description = models.TextField(max_length=400)
    is_available = models.BooleanField(default=True)
    duration_days = models.PositiveIntegerField(
        default=DEFAULT_MEMBERSHIP_DURATION_DAYS,
        help_text="Membership duration in days (typically 365 for one year)",
    )

    class Meta:
        verbose_name = "Membership tier"
        verbose_name_plural = "Membership tiers"
        ordering = ["price"]

    def __str__(self):
        return f"{self.name} ({self.price:,} RWF/year)"


# =========================
# User Membership
# =========================


class UserMembership(BaseModel):
    # =========================
    # Status
    # =========================
    STATUS_PENDING = "pending"
    STATUS_PAID = "paid"
    STATUS_ACTIVE = "active"
    STATUS_EXPIRED = "expired"
    STATUS_CANCELED = "canceled"

    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending Payment"),
        (STATUS_PAID, "Payment Received"),
        (STATUS_ACTIVE, "Active"),
        (STATUS_EXPIRED, "Expired"),
        (STATUS_CANCELED, "Canceled"),
    ]

    # =========================
    # Payment Modes
    # =========================
    PAYMENT_MOBILE_MONEY = "mobile_money"
    PAYMENT_CASH = "cash"
    PAYMENT_BANK = "bank"

    PAYMENT_MODE_CHOICES = [
        (PAYMENT_MOBILE_MONEY, "Mobile Money"),
        (PAYMENT_CASH, "Cash"),
        (PAYMENT_BANK, "Bank Transfer"),
    ]

    # =========================
    # Relations
    # =========================
    user = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="memberships",
    )
    membership = models.ForeignKey(
        Membership,
        on_delete=models.PROTECT,
        related_name="user_memberships",
    )

    # =========================
    # Membership State
    # =========================
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
    )

    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)

    # =========================
    # Payment Information
    # =========================
    payment_mode = models.CharField(
        max_length=20,
        choices=PAYMENT_MODE_CHOICES,
        null=True,
        blank=True,
    )

    payment_reference = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text="Mobile Money Tx ID, Bank slip number, or receipt reference",
    )

    amount_paid = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Amount paid in RWF (Rwandan Francs)",
    )

    payment_confirmed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="confirmed_memberships",
    )
    payment_confirmed_at = models.DateTimeField(null=True, blank=True)

    # =========================
    # Meta
    # =========================
    class Meta:
        ordering = ["-created_at"]
        constraints = [
            # Only one pending membership per user per membership type
            models.UniqueConstraint(
                fields=["user", "membership"],
                condition=Q(status="pending"),
                name="unique_pending_membership",
            ),
            # Only ONE active membership per user
            models.UniqueConstraint(
                fields=["user"],
                condition=Q(status="active"),
                name="unique_active_membership_per_user",
            ),
        ]
        indexes = [
            # Common lookups
            models.Index(fields=["user"], name="idx_membership_user"),
            models.Index(fields=["status"], name="idx_membership_status"),
            # Active membership lookup
            models.Index(fields=["user", "status"], name="idx_user_status"),
            # Expiration checks (cron / celery)
            models.Index(fields=["status", "end_date"], name="idx_status_end_date"),
            # Payment lookups
            models.Index(fields=["payment_reference"], name="idx_payment_reference"),
            models.Index(fields=["payment_mode"], name="idx_payment_mode"),
        ]

    # =========================
    # Validation
    # =========================

    def clean(self):
        super().clean()

        # Only one active membership allowed
        if self.status == self.STATUS_ACTIVE:
            active_exists = (
                UserMembership.objects.filter(user=self.user, status=self.STATUS_ACTIVE)
                .exclude(pk=self.pk)
                .exists()
            )
            if active_exists:
                raise ValidationError("User already has an active membership.")

        # Payment validation
        if self.status in [self.STATUS_PAID, self.STATUS_ACTIVE]:
            if not self.payment_mode:
                raise ValidationError("Payment mode is required.")

            if (
                self.payment_mode
                in [
                    self.PAYMENT_MOBILE_MONEY,
                    self.PAYMENT_BANK,
                ]
                and not self.payment_reference
            ):
                raise ValidationError(
                    "Payment reference is required for Mobile Money or Bank payments."
                )

            if not self.amount_paid:
                raise ValidationError("Amount paid is required.")

        # Date validation
        if self.start_date and self.end_date:
            if self.start_date >= self.end_date:
                raise ValidationError("End date must be after start date.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    # =========================
    # Business Logic
    # =========================

    @property
    def is_active(self):
        return (
            self.status == self.STATUS_ACTIVE
            and self.end_date
            and self.end_date > timezone.now()
        )

    @transaction.atomic
    def mark_as_paid(self, admin_user):
        if self.status != self.STATUS_PENDING:
            raise ValidationError("Only pending memberships can be marked as paid.")

        self.status = self.STATUS_PAID
        self.payment_confirmed_by = admin_user
        self.payment_confirmed_at = timezone.now()
        self.save()

    @transaction.atomic
    def activate(self, admin_user):
        """
        Activates this membership:
        - Expires any other active memberships
        - Sets start/end dates
        - Records payment confirmation
        """

        if self.status not in [self.STATUS_PAID, self.STATUS_PENDING]:
            raise ValidationError("Membership must be paid before activation.")

        # Expire other active memberships
        UserMembership.objects.filter(
            user=self.user,
            status=self.STATUS_ACTIVE,
        ).exclude(pk=self.pk).update(
            status=self.STATUS_EXPIRED,
            end_date=timezone.now(),
        )

        now = timezone.now()

        self.status = self.STATUS_ACTIVE
        self.start_date = now
        self.end_date = now + timedelta(days=self.membership.duration_days)
        self.payment_confirmed_by = admin_user
        self.payment_confirmed_at = now
        self.save()

    @transaction.atomic
    def cancel(self):
        if self.status not in [self.STATUS_PENDING, self.STATUS_PAID]:
            raise ValidationError("Only pending or paid memberships can be canceled.")

        self.status = self.STATUS_CANCELED
        self.end_date = timezone.now()
        self.save()

    @transaction.atomic
    def expire_if_needed(self):
        if self.status == self.STATUS_ACTIVE and self.end_date <= timezone.now():
            self.status = self.STATUS_EXPIRED
            self.save()
