"""
Default membership tier data for seeding. Tiers can be updated in Django Admin;
this is only used by create_sample_memberships and for initial data migrations.
Add or edit tiers here when changing the default offer, then run the seed command.
"""

# Default tiers to create if missing. max_order_price = max layaway (item value) for that tier.
DEFAULT_MEMBERSHIP_TIERS = [
    {
        "name": "Basic",
        "price": 10_000,
        "max_order_price": 30_000,
        "description": "Basic membership. Annual fee. Access to OLLEH layaway and savings. Max layaway 30,000 RWF.",
        "duration_days": 365,
        "is_available": True,
    },
    {
        "name": "Premium",
        "price": 20_000,
        "max_order_price": 50_000,
        "description": "Premium membership. Annual fee. Enhanced benefits. Max layaway 50,000 RWF.",
        "duration_days": 365,
        "is_available": True,
    },
]
