from django.db import models, transaction
from django.core.exceptions import ValidationError

from apps.common.models import BaseModel
from users.models import User


class SavingsAccount(BaseModel):
    """
    One savings account per member. Balance in RWF.
    Used to determine layaway limits and for refunds/penalties.
    """

    user = models.OneToOneField(
        User,
        on_delete=models.PROTECT,
        related_name="savings_account",
    )
    balance_rwf = models.PositiveIntegerField(
        default=0,
        help_text="Current balance in RWF (Rwandan Francs)",
    )

    class Meta:
        verbose_name = "Savings account"
        verbose_name_plural = "Savings accounts"

    def __str__(self):
        return f"{self.user.email} – {self.balance_rwf:,} RWF"

    @transaction.atomic
    def credit(self, amount_rwf, transaction_type, reference="", layaway=None):
        if amount_rwf <= 0:
            raise ValidationError("Credit amount must be positive.")
        self.balance_rwf += amount_rwf
        self.save(update_fields=["balance_rwf", "updated_at"])
        SavingsTransaction.objects.create(
            account=self,
            kind=transaction_type,
            amount_rwf=amount_rwf,
            reference=reference,
            layaway=layaway,
        )
        return self.balance_rwf

    @transaction.atomic
    def debit(self, amount_rwf, transaction_type, reference="", layaway=None):
        if amount_rwf <= 0:
            raise ValidationError("Debit amount must be positive.")
        if amount_rwf > self.balance_rwf:
            raise ValidationError(
                f"Insufficient balance. Available: {self.balance_rwf:,} RWF."
            )
        self.balance_rwf -= amount_rwf
        self.save(update_fields=["balance_rwf", "updated_at"])
        SavingsTransaction.objects.create(
            account=self,
            kind=transaction_type,
            amount_rwf=-amount_rwf,
            reference=reference,
            layaway=layaway,
        )
        return self.balance_rwf

    @classmethod
    def get_or_create_for_user(cls, user):
        account, _ = cls.objects.get_or_create(user=user, defaults={"balance_rwf": 0})
        return account


class SavingsTransaction(BaseModel):
    """
    Immutable log of savings movements.
    Positive amount = credit, negative = debit.
    """

    KIND_DEPOSIT = "deposit"
    KIND_WITHDRAWAL = "withdrawal"
    KIND_REFUND = "refund"
    KIND_LAYAWAY_PAYMENT = "layaway_payment"
    KIND_LAYAWAY_REFUND = "layaway_refund"
    KIND_PENALTY = "penalty"
    KIND_CANCEL_PENALTY = "cancel_penalty"

    KIND_CHOICES = [
        (KIND_DEPOSIT, "Deposit"),
        (KIND_WITHDRAWAL, "Withdrawal"),
        (KIND_REFUND, "Refund"),
        (KIND_LAYAWAY_PAYMENT, "Layaway payment"),
        (KIND_LAYAWAY_REFUND, "Layaway refund"),
        (KIND_PENALTY, "Penalty (payment failure)"),
        (KIND_CANCEL_PENALTY, "Cancellation penalty"),
    ]

    account = models.ForeignKey(
        SavingsAccount,
        on_delete=models.PROTECT,
        related_name="transactions",
    )
    kind = models.CharField(max_length=20, choices=KIND_CHOICES)
    amount_rwf = models.IntegerField(help_text="Positive = credit, negative = debit")
    reference = models.CharField(max_length=100, blank=True)
    # Layaway link for payment/refund/penalty (optional)
    layaway = models.ForeignKey(
        "orders.Layaway",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="savings_transactions",
    )

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(
                fields=["account", "created_at"], name="idx_savings_acc_created"
            )
        ]

    def __str__(self):
        return f"{self.account.user.email} {self.kind} {self.amount_rwf} RWF"


class RefundRequest(BaseModel):
    """
    Member requests withdrawal of savings. Processed within 7 working days per agreement.
    """

    STATUS_PENDING = "pending"
    STATUS_APPROVED = "approved"
    STATUS_REJECTED = "rejected"
    STATUS_PAID = "paid"

    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_APPROVED, "Approved"),
        (STATUS_REJECTED, "Rejected"),
        (STATUS_PAID, "Paid"),
    ]

    account = models.ForeignKey(
        SavingsAccount,
        on_delete=models.PROTECT,
        related_name="refund_requests",
    )
    amount_rwf = models.PositiveIntegerField()
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
    )
    reason = models.CharField(max_length=200, blank=True)
    admin_notes = models.TextField(blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Refund {self.amount_rwf} RWF – {self.status}"
