from django.db import models
from django.utils import timezone
from users.models import User
from apps.memberships.models import UserMembership


class Payment(models.Model):
    """
    Records a payment made by a user
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
        null=True,  # Optional: might track other payments too
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
