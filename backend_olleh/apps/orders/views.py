from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from drf_spectacular.utils import extend_schema, extend_schema_view

from apps.orders.models import Layaway, LayawayImage
from apps.orders.serializers import (
    LayawayListSerializer,
    LayawayDetailSerializer,
    LayawayCreateSerializer,
    LayawayEligibilitySerializer,
    LayawayImageSerializer,
    LayawayImageUploadSerializer,
    LayawayPaymentSerializer,
    LayawayPaymentCreateSerializer,
)
from apps.orders.services import get_layaway_eligibility
from apps.memberships.permissions import IsAuthenticatedClient, IsOwnerOrAdmin
from apps.payments.models import LayawayPayment
from apps.payments.services import confirm_layaway_payment


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
        serializer = LayawayCreateSerializer(
            data=request.data, context={"request": request}
        )
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
            seller_name=data.get("seller_name", ""),
            seller_phone=data.get("seller_phone", ""),
            seller_address=data.get("seller_address", ""),
        )
        return Response(
            LayawayDetailSerializer(layaway, context={"request": request}).data,
            status=status.HTTP_201_CREATED,
        )

    @extend_schema(
        summary="Add item image",
        description="Upload an image of the requested item (multipart: image=file, caption=optional, order=optional).",
        tags=["Client - Layaways"],
        request=LayawayImageUploadSerializer,
        responses={201: LayawayImageSerializer},
    )
    @action(detail=True, methods=["post"], url_path="images")
    def add_image(self, request, pk=None):
        layaway = self.get_object()
        serializer = LayawayImageUploadSerializer(
            data=request.data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save(layaway=layaway)
        # Return with full URL
        out = LayawayImageSerializer(
            serializer.instance,
            context={"request": request},
        )
        return Response(out.data, status=status.HTTP_201_CREATED)

    @extend_schema(
        summary="List layaway payments",
        description="List all payments reported for this layaway.",
        tags=["Client - Layaways"],
        responses={200: LayawayPaymentSerializer(many=True)},
    )
    @extend_schema(
        methods=["POST"],
        summary="Report a payment",
        description="Report that you made a payment toward this layaway. Staff will confirm; then the amount is applied and layaway status may update when paid in full.",
        request=LayawayPaymentCreateSerializer,
        responses={201: LayawayPaymentSerializer},
    )
    @action(detail=True, methods=["get", "post"], url_path="payments")
    def payments(self, request, pk=None):
        layaway = self.get_object()
        if request.method == "GET":
            qs = layaway.payments.all()
            serializer = LayawayPaymentSerializer(qs, many=True)
            return Response(serializer.data)
        # POST: report payment
        if layaway.status not in (
            Layaway.STATUS_ACTIVE,
            Layaway.STATUS_COOLING_OFF,
        ):
            return Response(
                {
                    "detail": "Payments can only be reported for active or cooling-off layaways."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer = LayawayPaymentCreateSerializer(
            data=request.data,
            context={"request": request, "layaway": layaway},
        )
        serializer.is_valid(raise_exception=True)
        payment = serializer.save(layaway=layaway)
        out = LayawayPaymentSerializer(payment)
        return Response(out.data, status=status.HTTP_201_CREATED)

    @extend_schema(
        summary="Confirm a payment (staff)",
        description="Confirm a reported payment. Amount is applied to the layaway; if paid in full, layaway is marked completed.",
        tags=["Staff - Layaways"],
        responses={200: LayawayDetailSerializer},
    )
    @action(
        detail=True,
        methods=["post"],
        url_path=r"payments/(?P<payment_id>[^/.]+)/confirm",
        permission_classes=[IsAuthenticatedClient, IsOwnerOrAdmin, IsAdminUser],
    )
    def confirm_payment(self, request, pk=None, payment_id=None):
        layaway = self.get_object()
        try:
            payment = layaway.payments.get(pk=payment_id)
        except LayawayPayment.DoesNotExist:
            return Response(
                {"detail": "Payment not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        try:
            confirm_layaway_payment(payment, confirmed_by=request.user)
        except Exception as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(
            LayawayDetailSerializer(layaway, context={"request": request}).data,
            status=status.HTTP_200_OK,
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
                    + (
                        " No penalty (within cooling-off period)."
                        if in_cooling
                        else f" Cancellation penalty of {instance.cancellation_penalty_rwf:,} RWF applies."
                    )
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
