from datetime import timedelta

from django.db import models, transaction
from django.utils import timezone
from django.core.exceptions import ValidationError

from apps.common.models import BaseModel
from users.models import User


# ---------- Constants (OLLEH agreement) ----------
LAYAWAY_MIN_DAYS = 14
LAYAWAY_MAX_DAYS = 30
COOLING_OFF_HOURS = 48
SERVICE_FEE_FLAT_THRESHOLD_RWF = 50_000
SERVICE_FEE_FLAT_AMOUNT_RWF = 5_000
SERVICE_FEE_PERCENT_ABOVE_THRESHOLD = 10  # 10%
CANCELLATION_PENALTY_RWF = 10_000
DEFAULT_PENALTY_RWF = 10_000  # Payment failure penalty


def compute_service_fee_rwf(item_value_rwf):
    """Items ≤50k RWF: 5,000 RWF flat. Above: 10%."""
    if item_value_rwf <= SERVICE_FEE_FLAT_THRESHOLD_RWF:
        return SERVICE_FEE_FLAT_AMOUNT_RWF
    return (item_value_rwf * SERVICE_FEE_PERCENT_ABOVE_THRESHOLD) // 100


def get_layaway_limit_rwf(savings_balance_rwf):
    """
    Layaway limit based on savings (OLLEH rules charter):
    - 0 RWF savings → 30,000 RWF
    - 1–30,000 RWF → 2× savings
    - 30,001–60,000 RWF → 80,000 RWF
    - 60,001+ RWF → 120,000 RWF
    """
    if savings_balance_rwf <= 0:
        return 30_000
    if savings_balance_rwf <= 30_000:
        return 2 * savings_balance_rwf
    if savings_balance_rwf <= 60_000:
        return 80_000
    return 120_000


class Layaway(BaseModel):
    """
    A layaway reservation: member reserves an item and pays over 14–30 days.
    Item remains OLLEH property until fully paid.
    """

    STATUS_PENDING_CONFIRMATION = "pending_confirmation"
    STATUS_COOLING_OFF = "cooling_off"
    STATUS_ACTIVE = "active"
    STATUS_COMPLETED = "completed"
    STATUS_CANCELED = "canceled"
    STATUS_DEFAULTED = "defaulted"

    STATUS_CHOICES = [
        (STATUS_PENDING_CONFIRMATION, "Pending confirmation"),
        (STATUS_COOLING_OFF, "Cooling off (48h)"),
        (STATUS_ACTIVE, "Active"),
        (STATUS_COMPLETED, "Completed"),
        (STATUS_CANCELED, "Canceled"),
        (STATUS_DEFAULTED, "Defaulted"),
    ]

    COLLECTION_PICKUP = "pickup"
    COLLECTION_DELIVERY = "delivery"

    COLLECTION_CHOICES = [
        (COLLECTION_PICKUP, "Pick up at OLLEH office (free)"),
        (COLLECTION_DELIVERY, "Delivery (fee separate)"),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="layaways",
    )
    item_description = models.CharField(max_length=300, blank=True)
    item_value_rwf = models.PositiveIntegerField(
        help_text="Agreed item price in RWF"
    )
    service_fee_rwf = models.PositiveIntegerField(
        help_text="Service & protection fee in RWF"
    )
    total_rwf = models.PositiveIntegerField(
        help_text="item_value_rwf + service_fee_rwf"
    )
    delivery_fee_rwf = models.PositiveIntegerField(default=0)

    status = models.CharField(
        max_length=24,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING_CONFIRMATION,
    )
    collection_type = models.CharField(
        max_length=20,
        choices=COLLECTION_CHOICES,
        default=COLLECTION_PICKUP,
    )

    # Dates: 14–30 days from confirmation
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    duration_days = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Agreed layaway period in days (14–30)",
    )

    # When OLLEH secured the item (starts cooling-off or active)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    cooling_off_until = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Until this time member can cancel without penalty",
    )

    # Payments
    amount_paid_rwf = models.PositiveIntegerField(default=0)

    # Penalties applied
    cancellation_penalty_rwf = models.PositiveIntegerField(default=0)
    default_penalty_rwf = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "status"], name="idx_layaway_user_status"),
            models.Index(fields=["status", "end_date"], name="idx_layaway_status_end"),
        ]
        verbose_name = "Layaway"
        verbose_name_plural = "Layaways"

    def __str__(self):
        return f"Layaway #{self.id} – {self.user.email} – {self.total_rwf:,} RWF"

    def save(self, *args, **kwargs):
        if self.item_value_rwf and not self.service_fee_rwf:
            self.service_fee_rwf = compute_service_fee_rwf(self.item_value_rwf)
        if self.item_value_rwf is not None and self.service_fee_rwf is not None:
            self.total_rwf = self.item_value_rwf + self.service_fee_rwf + self.delivery_fee_rwf
        super().save(*args, **kwargs)

    @property
    def is_in_cooling_off(self):
        if not self.cooling_off_until:
            return False
        return timezone.now() <= self.cooling_off_until and self.status in (
            self.STATUS_COOLING_OFF,
            self.STATUS_ACTIVE,
        )

    @property
    def can_cancel_without_penalty(self):
        return self.is_in_cooling_off and self.status != self.STATUS_CANCELED

    @transaction.atomic
    def confirm_by_olleh(self):
        """OLLEH secured the item: set cooling-off period and optionally activate."""
        if self.status != self.STATUS_PENDING_CONFIRMATION:
            raise ValidationError("Only pending layaways can be confirmed.")
        now = timezone.now()
        self.confirmed_at = now
        self.cooling_off_until = now + timedelta(hours=COOLING_OFF_HOURS)
        self.status = self.STATUS_COOLING_OFF
        self.save()

    @transaction.atomic
    def activate(self, duration_days=None):
        """Move to active and set end date (14–30 days)."""
        if self.status not in (self.STATUS_COOLING_OFF, self.STATUS_PENDING_CONFIRMATION):
            raise ValidationError("Layaway must be in cooling-off or pending to activate.")
        if duration_days is None:
            duration_days = LAYAWAY_MAX_DAYS
        if not (LAYAWAY_MIN_DAYS <= duration_days <= LAYAWAY_MAX_DAYS):
            raise ValidationError(
                f"Duration must be between {LAYAWAY_MIN_DAYS} and {LAYAWAY_MAX_DAYS} days."
            )
        now = timezone.now()
        self.start_date = self.confirmed_at or now
        self.end_date = self.start_date + timedelta(days=duration_days)
        self.duration_days = duration_days
        self.status = self.STATUS_ACTIVE
        if not self.cooling_off_until:
            self.cooling_off_until = now + timedelta(hours=COOLING_OFF_HOURS)
        self.save()

    @transaction.atomic
    def cancel(self, apply_penalty=True):
        """Cancel layaway. If after cooling-off, apply 10k penalty."""
        if self.status in (self.STATUS_CANCELED, self.STATUS_COMPLETED, self.STATUS_DEFAULTED):
            raise ValidationError("This layaway cannot be canceled.")
        if apply_penalty and not self.can_cancel_without_penalty:
            self.cancellation_penalty_rwf = CANCELLATION_PENALTY_RWF
        self.status = self.STATUS_CANCELED
        self.save()

    @transaction.atomic
    def mark_completed(self):
        if self.status != self.STATUS_ACTIVE:
            raise ValidationError("Only active layaways can be completed.")
        if self.amount_paid_rwf < self.total_rwf:
            raise ValidationError("Full payment required to complete.")
        self.status = self.STATUS_COMPLETED
        self.save()

    @transaction.atomic
    def mark_defaulted(self):
        """Payment not completed in time. Item returned to market; penalty applies."""
        if self.status != self.STATUS_ACTIVE:
            raise ValidationError("Only active layaways can be marked defaulted.")
        self.status = self.STATUS_DEFAULTED
        self.default_penalty_rwf = DEFAULT_PENALTY_RWF
        self.save()
