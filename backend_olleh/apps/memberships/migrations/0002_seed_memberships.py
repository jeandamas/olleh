# Data migration: seed OLLEH membership tiers (Basic 10k, Premium 20k RWF/year)

from django.db import migrations


def seed_memberships(apps, schema_editor):
    Membership = apps.get_model("memberships", "Membership")
    tiers = [
        {
            "name": "Basic",
            "price": 10_000,
            "max_order_price": 100_000,
            "description": "Basic membership. Annual fee. Access to OLLEH layaway and savings services.",
            "duration_days": 365,
            "is_available": True,
        },
        {
            "name": "Premium",
            "price": 20_000,
            "max_order_price": 500_000,
            "description": "Premium membership. Annual fee. Enhanced benefits and higher limits.",
            "duration_days": 365,
            "is_available": True,
        },
    ]
    for data in tiers:
        Membership.objects.get_or_create(
            name=data["name"],
            defaults={
                "price": data["price"],
                "max_order_price": data["max_order_price"],
                "description": data["description"],
                "duration_days": data["duration_days"],
                "is_available": data["is_available"],
            },
        )


def noop_reverse(apps, schema_editor):
    # Do not delete seeded memberships on reverse (they may have user_memberships)
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("memberships", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed_memberships, noop_reverse),
    ]
