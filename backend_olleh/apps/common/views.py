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
from apps.memberships.permissions import IsAuthenticatedClient


class PoliciesViewSet(GenericViewSet):
    """
    Read-only OLLEH policy constants for the app (fees, limits, cooling-off, etc.).
    """

    permission_classes = []  # public
    authentication_classes = []  # allow unauthenticated read for policy display

    @extend_schema(
        summary="Get OLLEH policies",
        description="Returns policy constants: layaway days, service fees, penalties, cooling-off.",
        tags=["Public - Policies"],
        responses={200: None},
    )
    def list(self, request):
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
                "savings_to_layaway_limits": {
                    "0_rwf": 30_000,
                    "1_to_30k": "2× savings",
                    "30k_to_60k_rwf": 80_000,
                    "60k_plus_rwf": 120_000,
                },
            }
        )
