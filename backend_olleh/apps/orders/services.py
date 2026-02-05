"""
Layaway eligibility and limits per OLLEH agreement.
"""

from django.db.models import Sum

from apps.memberships.models import UserMembership
from apps.orders.models import Layaway, get_layaway_limit_rwf
from apps.savings.models import SavingsAccount


def get_member_savings_balance_rwf(user):
    """Return member's savings balance in RWF (0 if no account)."""
    try:
        return user.savings_account.balance_rwf
    except SavingsAccount.DoesNotExist:
        return 0


def get_layaway_eligibility(user):
    """
    Returns dict: has_active_membership, savings_balance_rwf, layaway_limit_rwf,
    current_layaway_total_rwf (sum of item_value for active layaways), can_request (bool),
    message (str).
    """
    from django.utils import timezone

    has_active_membership = (
        UserMembership.objects.filter(
            user=user,
            status=UserMembership.STATUS_ACTIVE,
        )
        .filter(end_date__gt=timezone.now())
        .exists()
    )

    savings_balance_rwf = get_member_savings_balance_rwf(user)
    layaway_limit_rwf = get_layaway_limit_rwf(savings_balance_rwf)

    current_layaway_total_rwf = (
        Layaway.objects.filter(
            user=user,
            status__in=[Layaway.STATUS_PENDING_CONFIRMATION, Layaway.STATUS_COOLING_OFF, Layaway.STATUS_ACTIVE],
        ).aggregate(total=Sum("item_value_rwf"))["total"]
        or 0
    )

    available_rwf = max(0, layaway_limit_rwf - current_layaway_total_rwf)
    can_request = has_active_membership and available_rwf > 0

    if not has_active_membership:
        message = "Active OLLEH membership is required to request a layaway."
    elif available_rwf <= 0:
        message = (
            f"Your layaway limit ({layaway_limit_rwf:,} RWF) is already used. "
            "Increase savings to raise your limit."
        )
    else:
        message = (
            f"You can request a layaway up to {available_rwf:,} RWF (item value) "
            f"within your limit of {layaway_limit_rwf:,} RWF."
        )

    return {
        "has_active_membership": has_active_membership,
        "savings_balance_rwf": savings_balance_rwf,
        "layaway_limit_rwf": layaway_limit_rwf,
        "current_layaway_total_rwf": current_layaway_total_rwf,
        "available_layaway_rwf": available_rwf,
        "can_request": can_request,
        "message": message,
    }
