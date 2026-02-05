# Generated manually for OLLEH agreement

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="MemberProfile",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("olleh_code", models.CharField(blank=True, help_text="Unique OLLEH member ID/code (auto-generated if empty)", max_length=20, unique=True)),
                ("reputation", models.CharField(choices=[("starter", "Starter"), ("trusted", "Trusted"), ("elite", "Elite")], default="starter", max_length=20)),
                ("phone", models.CharField(blank=True, max_length=20)),
                ("national_id", models.CharField(blank=True, max_length=50)),
                ("full_name", models.CharField(blank=True, max_length=150)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("user", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="member_profile", to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "verbose_name": "Member profile",
                "verbose_name_plural": "Member profiles",
            },
        ),
        migrations.CreateModel(
            name="MemberMeasurements",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("height_cm", models.PositiveSmallIntegerField(blank=True, null=True)),
                ("chest_cm", models.PositiveSmallIntegerField(blank=True, null=True)),
                ("waist_cm", models.PositiveSmallIntegerField(blank=True, null=True)),
                ("hip_cm", models.PositiveSmallIntegerField(blank=True, null=True)),
                ("shoe_size_eu", models.DecimalField(blank=True, decimal_places=1, max_digits=4, null=True)),
                ("notes", models.CharField(blank=True, max_length=200)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("user", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="measurements", to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "verbose_name": "Member measurements",
                "verbose_name_plural": "Member measurements",
            },
        ),
    ]
