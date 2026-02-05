from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from drf_spectacular.utils import extend_schema

from apps.orders.models import (
    LAYAWAY_MIN_DAYS,
    LAYAWAY_MAX_DAYS,
    COOLING_OFF_HOURS,
    SERVICE_FEE_FLAT_THRESHOLD_RWF,
    SERVICE_FEE_FLAT_AMOUNT_RWF,
    SERVICE_FEE_PERCENT_ABOVE_THRESHOLD,
    CANCELLATION_PENALTY_RWF,
    DEFAULT_PENALTY_RWF,
)
from apps.memberships.models import Membership


class PoliciesViewSet(GenericViewSet):
    """
    Read-only OLLEH policy constants. Membership tiers and limits come from DB so they can be updated without code changes.
    """

    permission_classes = []  # public
    authentication_classes = []  # allow unauthenticated read for policy display

    @extend_schema(
        summary="Get OLLEH policies",
        description="Returns policy constants and current membership tiers (from DB). Edit tiers in Admin to change limits.",
        tags=["Public - Policies"],
        responses={200: None},
    )
    def list(self, request):
        # Membership tiers from DB: name, price, max layaway (no hardcoded tier names or limits)
        membership_tiers = list(
            Membership.objects.filter(is_available=True)
            .order_by("price")
            .values("name", "price", "max_order_price", "duration_days")
        )
        return Response(
            {
                "layaway": {
                    "min_days": LAYAWAY_MIN_DAYS,
                    "max_days": LAYAWAY_MAX_DAYS,
                    "cooling_off_hours": COOLING_OFF_HOURS,
                },
                "service_fee": {
                    "item_value_threshold_rwf": SERVICE_FEE_FLAT_THRESHOLD_RWF,
                    "flat_fee_rwf": SERVICE_FEE_FLAT_AMOUNT_RWF,
                    "percent_above_threshold": SERVICE_FEE_PERCENT_ABOVE_THRESHOLD,
                    "description": f"Items ≤{SERVICE_FEE_FLAT_THRESHOLD_RWF:,} RWF: {SERVICE_FEE_FLAT_AMOUNT_RWF:,} RWF flat. Above: {SERVICE_FEE_PERCENT_ABOVE_THRESHOLD}%.",
                },
                "penalties": {
                    "cancellation_penalty_rwf": CANCELLATION_PENALTY_RWF,
                    "default_penalty_rwf": DEFAULT_PENALTY_RWF,
                },
                "membership_tiers": {
                    "description": "Max layaway (item value) = max_order_price of the active membership tier. Edit tiers in Admin to change.",
                    "tiers": membership_tiers,
                },
            }
        )
