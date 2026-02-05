# Generated manually for OLLEH savings

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("orders", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="SavingsAccount",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("balance_rwf", models.PositiveIntegerField(default=0, help_text="Current balance in RWF (Rwandan Francs)")),
                ("user", models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, related_name="savings_account", to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "verbose_name": "Savings account",
                "verbose_name_plural": "Savings accounts",
            },
        ),
        migrations.CreateModel(
            name="RefundRequest",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("amount_rwf", models.PositiveIntegerField()),
                ("status", models.CharField(choices=[("pending", "Pending"), ("approved", "Approved"), ("rejected", "Rejected"), ("paid", "Paid")], default="pending", max_length=20)),
                ("reason", models.CharField(blank=True, max_length=200)),
                ("admin_notes", models.TextField(blank=True)),
                ("account", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="refund_requests", to="savings.savingsaccount")),
            ],
            options={
                "ordering": ["-created_at"],
            },
        ),
        migrations.CreateModel(
            name="SavingsTransaction",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("kind", models.CharField(choices=[("deposit", "Deposit"), ("withdrawal", "Withdrawal"), ("refund", "Refund"), ("layaway_payment", "Layaway payment"), ("layaway_refund", "Layaway refund"), ("penalty", "Penalty (payment failure)"), ("cancel_penalty", "Cancellation penalty")], max_length=20)),
                ("amount_rwf", models.IntegerField(help_text="Positive = credit, negative = debit")),
                ("reference", models.CharField(blank=True, max_length=100)),
                ("account", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="transactions", to="savings.savingsaccount")),
                ("layaway", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="savings_transactions", to="orders.layaway")),
            ],
            options={
                "ordering": ["-created_at"],
            },
        ),
        migrations.AddIndex(
            model_name="savingstransaction",
            index=models.Index(fields=["account", "created_at"], name="idx_savings_acc_created"),
        ),
    ]
