from django.db import models
from users.models import User
from apps.memberships.models import UserMembership


class Payment(models.Model):
    """
    Records a payment made by a user (e.g. membership fee).
    """

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("completed", "Completed"),
        ("failed", "Failed"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="payments")
    membership = models.ForeignKey(
        UserMembership,
        on_delete=models.CASCADE,
        related_name="payments",
        null=True,
        blank=True,
    )
    amount = models.PositiveIntegerField()
    reference = models.CharField(
        max_length=100, unique=True, help_text="Unique transaction reference"
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)
    paid_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Payment"
        verbose_name_plural = "Payments"

    def __str__(self):
        return f"{self.user.email} - {self.amount} RWF - {self.get_status_display()}"

    @property
    def is_paid(self):
        return self.status == "completed" and self.paid_at is not None


class LayawayPayment(models.Model):
    """
    A payment reported by a member toward a layaway. No status field:
    member reports payment → staff confirms (confirmed_at/confirmed_by).
    When confirmed, amount is applied to layaway.amount_paid_rwf and
    layaway may be marked completed if paid in full.
    """

    layaway = models.ForeignKey(
        "orders.Layaway",
        on_delete=models.CASCADE,
        related_name="payments",
    )
    amount_rwf = models.PositiveIntegerField(help_text="Amount paid in RWF")
    reference = models.CharField(
        max_length=100,
        blank=True,
        help_text="Optional transaction reference (e.g. Mobile Money code)",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    # Staff confirmation (no separate status: unconfirmed = null confirmed_at)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    confirmed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="confirmed_layaway_payments",
    )

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Layaway payment"
        verbose_name_plural = "Layaway payments"

    def __str__(self):
        return f"Layaway #{self.layaway_id} – {self.amount_rwf:,} RWF"

    @property
    def is_confirmed(self):
        return self.confirmed_at is not None
