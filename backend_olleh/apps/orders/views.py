from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, extend_schema_view

from apps.orders.models import Layaway
from apps.orders.serializers import (
    LayawayListSerializer,
    LayawayDetailSerializer,
    LayawayCreateSerializer,
    LayawayEligibilitySerializer,
)
from apps.orders.services import get_layaway_eligibility
from apps.memberships.permissions import IsAuthenticatedClient, IsOwnerOrAdmin


@extend_schema_view(
    list=extend_schema(
        summary="List my layaways",
        description="List all layaways for the authenticated member.",
        tags=["Client - Layaways"],
    ),
    retrieve=extend_schema(
        summary="Get layaway details",
        tags=["Client - Layaways"],
    ),
)
class LayawayViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticatedClient, IsOwnerOrAdmin]
    http_method_names = ["get", "post", "delete", "head", "options"]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff or user.is_superuser:
            return Layaway.objects.all()
        return Layaway.objects.filter(user=user)

    def get_serializer_class(self):
        if self.action == "create":
            return LayawayCreateSerializer
        if self.action == "list":
            return LayawayListSerializer
        return LayawayDetailSerializer

    def create(self, request, *args, **kwargs):
        serializer = LayawayCreateSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        layaway = Layaway.objects.create(
            user=request.user,
            item_description=data.get("item_description", ""),
            item_value_rwf=data["item_value_rwf"],
            service_fee_rwf=0,  # computed in save()
            delivery_fee_rwf=data.get("delivery_fee_rwf", 0),
            collection_type=data.get("collection_type", Layaway.COLLECTION_PICKUP),
            status=Layaway.STATUS_PENDING_CONFIRMATION,
        )
        return Response(
            LayawayDetailSerializer(layaway).data,
            status=status.HTTP_201_CREATED,
        )

    def destroy(self, request, *args, **kwargs):
        """Cancel layaway. Penalty applied if outside cooling-off."""
        instance = self.get_object()
        try:
            in_cooling = instance.can_cancel_without_penalty
            instance.cancel(apply_penalty=not in_cooling)
            return Response(
                {
                    "detail": "Layaway canceled."
                    + (" No penalty (within cooling-off period)." if in_cooling else f" Cancellation penalty of {instance.cancellation_penalty_rwf:,} RWF applies.")
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

    @extend_schema(
        summary="Get layaway eligibility",
        description="Get your current layaway limit, savings balance, and whether you can request a new layaway.",
        tags=["Client - Layaways"],
        responses={200: LayawayEligibilitySerializer},
    )
    @action(detail=False, methods=["get"])
    def eligibility(self, request):
        eligibility = get_layaway_eligibility(request.user)
        return Response(LayawayEligibilitySerializer(eligibility).data)
