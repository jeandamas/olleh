# Generated manually for OLLEH layaway

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Layaway",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("item_description", models.CharField(blank=True, max_length=300)),
                (
                    "item_value_rwf",
                    models.PositiveIntegerField(help_text="Agreed item price in RWF"),
                ),
                (
                    "service_fee_rwf",
                    models.PositiveIntegerField(
                        help_text="Service & protection fee in RWF"
                    ),
                ),
                (
                    "total_rwf",
                    models.PositiveIntegerField(
                        help_text="item_value_rwf + service_fee_rwf"
                    ),
                ),
                ("delivery_fee_rwf", models.PositiveIntegerField(default=0)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("pending_confirmation", "Pending confirmation"),
                            ("cooling_off", "Cooling off (48h)"),
                            ("active", "Active"),
                            ("completed", "Completed"),
                            ("canceled", "Canceled"),
                            ("defaulted", "Defaulted"),
                        ],
                        default="pending_confirmation",
                        max_length=24,
                    ),
                ),
                (
                    "collection_type",
                    models.CharField(
                        choices=[
                            ("pickup", "Pick up at OLLEH office (free)"),
                            ("delivery", "Delivery (fee separate)"),
                        ],
                        default="pickup",
                        max_length=20,
                    ),
                ),
                ("start_date", models.DateTimeField(blank=True, null=True)),
                ("end_date", models.DateTimeField(blank=True, null=True)),
                (
                    "duration_days",
                    models.PositiveIntegerField(
                        blank=True,
                        help_text="Agreed layaway period in days (14–30)",
                        null=True,
                    ),
                ),
                ("confirmed_at", models.DateTimeField(blank=True, null=True)),
                (
                    "cooling_off_until",
                    models.DateTimeField(
                        blank=True,
                        help_text="Until this time member can cancel without penalty",
                        null=True,
                    ),
                ),
                ("amount_paid_rwf", models.PositiveIntegerField(default=0)),
                ("cancellation_penalty_rwf", models.PositiveIntegerField(default=0)),
                ("default_penalty_rwf", models.PositiveIntegerField(default=0)),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="layaways",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ["-created_at"],
                "verbose_name": "Layaway",
                "verbose_name_plural": "Layaways",
            },
        ),
        migrations.AddIndex(
            model_name="layaway",
            index=models.Index(
                fields=["user", "status"], name="idx_layaway_user_status"
            ),
        ),
        migrations.AddIndex(
            model_name="layaway",
            index=models.Index(
                fields=["status", "end_date"], name="idx_layaway_status_end"
            ),
        ),
    ]
