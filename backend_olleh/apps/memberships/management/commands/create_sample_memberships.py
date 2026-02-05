"""
Seed membership tiers from apps.memberships.constants. Idempotent.
Tiers can be updated later in Django Admin; limits and pricing are stored in DB.
"""

from django.core.management.base import BaseCommand

from apps.memberships.constants import DEFAULT_MEMBERSHIP_TIERS
from apps.memberships.models import Membership


class Command(BaseCommand):
    help = "Seed default membership tiers from constants. Idempotent. Edit tiers in Admin after."

    def handle(self, *args, **options):
        created_count = 0
        skipped_count = 0

        for data in DEFAULT_MEMBERSHIP_TIERS:
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
            self.style.SUCCESS(
                f"\nDone. {created_count} created, {skipped_count} unchanged."
            )
        )
