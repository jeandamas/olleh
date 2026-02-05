"""
Seed OLLEH membership tiers (Basic 10,000 RWF, Premium 20,000 RWF per year).
Idempotent: safe to run multiple times. Matches OLLEH Membership & Layaway Agreement.
"""

from django.core.management.base import BaseCommand

from apps.memberships.models import Membership


MEMBERSHIPS_DATA = [
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


class Command(BaseCommand):
    help = "Seed OLLEH membership tiers (Basic 10k, Premium 20k RWF/year). Idempotent."

    def handle(self, *args, **options):
        created_count = 0
        skipped_count = 0

        for data in MEMBERSHIPS_DATA:
            membership, created = Membership.objects.get_or_create(
                name=data["name"],
                defaults={
                    "price": data["price"],
                    "max_order_price": data["max_order_price"],
                    "description": data["description"],
                    "duration_days": data["duration_days"],
                    "is_available": data["is_available"],
                },
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Created: {membership.name} ({membership.price:,} RWF/year)"
                    )
                )
                created_count += 1
            else:
                self.stdout.write(
                    self.style.WARNING(f"Already exists: {membership.name}")
                )
                skipped_count += 1

        self.stdout.write(
            self.style.SUCCESS(f"\nDone. {created_count} created, {skipped_count} unchanged.")
        )
