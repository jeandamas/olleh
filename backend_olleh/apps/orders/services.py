"""
Layaway eligibility and limits: from active membership tier only (no savings-based cap).
Only one active membership per user (enforced by unique constraint).
"""

from django.db.models import Sum

from apps.memberships.models import UserMembership
from apps.orders.models import Layaway
from apps.savings.models import SavingsAccount


def get_member_savings_balance_rwf(user):
    """Return member's savings balance in RWF (0 if no account). Display only; not used for limit."""
    try:
        return user.savings_account.balance_rwf
    except SavingsAccount.DoesNotExist:
        return 0


def get_active_membership_for_user(user):
    """
    Return the user's single active (non-expired) membership, or None.
    Uses UserMembership.get_active_for_user (only one active per user).
    """
    return UserMembership.get_active_for_user(user)


def get_layaway_eligibility(user):
    """
    Returns dict: has_active_membership, savings_balance_rwf, layaway_limit_rwf,
    current_layaway_total_rwf, available_layaway_rwf, can_request, message.
    Layaway limit comes from active membership tier max_order_price only (no savings cap).
    """
    active_membership = get_active_membership_for_user(user)
    has_active_membership = active_membership is not None
    layaway_limit_rwf = (
        active_membership.membership.max_order_price if active_membership else 0
    )

    savings_balance_rwf = get_member_savings_balance_rwf(user)

    current_layaway_total_rwf = (
        Layaway.objects.filter(
            user=user,
            status__in=[
                Layaway.STATUS_PENDING_CONFIRMATION,
                Layaway.STATUS_COOLING_OFF,
                Layaway.STATUS_ACTIVE,
            ],
        ).aggregate(total=Sum("item_value_rwf"))["total"]
        or 0
    )

    available_rwf = max(0, layaway_limit_rwf - current_layaway_total_rwf)
    can_request = has_active_membership and available_rwf > 0

    if not has_active_membership:
        message = "Active OLLEH membership is required to request a layaway."
    elif available_rwf <= 0:
        message = f"Your layaway limit ({layaway_limit_rwf:,} RWF) is already used."
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
