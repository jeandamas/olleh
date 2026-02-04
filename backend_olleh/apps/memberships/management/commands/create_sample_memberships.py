from django.core.management.base import BaseCommand
from apps.memberships.models import Membership


class Command(BaseCommand):
    help = "Create sample membership tiers for testing"

    def handle(self, *args, **kwargs):
        # Sample membership tiers data (all prices in RWF - integers only)
        memberships_data = [
            {
                "name": "Bronze",
                "price": 25000,
                "max_order_price": 50000,
                "description": "Perfect for occasional shoppers. Get started with basic membership benefits and enjoy exclusive access to our platform.",
                "duration_days": 365,
                "is_available": True,
            },
            {
                "name": "Silver",
                "price": 50000,
                "max_order_price": 150000,
                "description": "Great for regular customers. Enhanced benefits with higher order limits and priority support.",
                "duration_days": 365,
                "is_available": True,
            },
            {
                "name": "Gold",
                "price": 100000,
                "max_order_price": 500000,
                "description": "Premium membership for serious buyers. Maximum order limits, premium support, and exclusive deals.",
                "duration_days": 365,
                "is_available": True,
            },
            {
                "name": "Platinum",
                "price": 250000,
                "max_order_price": 2000000,
                "description": "Ultimate membership for power users. Unlimited benefits, VIP support, and the highest order limits available.",
                "duration_days": 365,
                "is_available": True,
            },
        ]

        created_count = 0
        skipped_count = 0

        for membership_data in memberships_data:
            membership, created = Membership.objects.get_or_create(
                name=membership_data["name"],
                defaults={
                    "price": membership_data["price"],
                    "max_order_price": membership_data["max_order_price"],
                    "description": membership_data["description"],
                    "duration_days": membership_data["duration_days"],
                    "is_available": membership_data["is_available"],
                },
            )

            if created:
                self.stdout.write(
                    self.style.SUCCESS(
                        f"✓ Created membership: {membership.name} ({membership.price:,} RWF)"
                    )
                )
                created_count += 1
            else:
                self.stdout.write(
                    self.style.WARNING(f"⚠ Skipped (already exists): {membership.name}")
                )
                skipped_count += 1

        self.stdout.write("\n" + "=" * 60)
        self.stdout.write(
            self.style.SUCCESS(
                f"Summary: {created_count} created, {skipped_count} skipped"
            )
        )
        self.stdout.write("=" * 60)
