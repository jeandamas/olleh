from rest_framework import serializers

from apps.orders.models import (
    Layaway,
    LayawayImage,
    compute_service_fee_rwf,
    LAYAWAY_MIN_DAYS,
    LAYAWAY_MAX_DAYS,
)
from apps.orders.services import get_layaway_eligibility
from apps.payments.models import LayawayPayment


class LayawayImageSerializer(serializers.ModelSerializer):
    """Read-only serializer for layaway item images; image URL is absolute."""

    url = serializers.SerializerMethodField()

    class Meta:
        model = LayawayImage
        fields = ["id", "url", "caption", "order", "created_at"]
        read_only_fields = fields

    def get_url(self, obj):
        if not obj.image:
            return None
        request = self.context.get("request")
        if request:
            return request.build_absolute_uri(obj.image.url)
        return obj.image.url


class LayawayImageUploadSerializer(serializers.ModelSerializer):
    """Upload an item image for a layaway. Use multipart/form-data: image (file), caption (optional), order (optional)."""

    class Meta:
        model = LayawayImage
        fields = ["id", "image", "caption", "order"]
        extra_kwargs = {
            "image": {
                "required": True,
                "help_text": "Image file (JPEG, PNG, GIF, WebP). Required.",
            },
            "caption": {
                "required": False,
                "allow_blank": True,
                "help_text": "Optional caption for the image.",
            },
            "order": {
                "required": False,
                "default": 0,
                "help_text": "Display order (lower first). Default 0.",
            },
        }


class LayawayPaymentSerializer(serializers.ModelSerializer):
    """Read-only serializer for a layaway payment."""

    is_confirmed = serializers.BooleanField(read_only=True)

    class Meta:
        model = LayawayPayment
        fields = [
            "id",
            "amount_rwf",
            "reference",
            "created_at",
            "confirmed_at",
            "confirmed_by",
            "is_confirmed",
        ]
        read_only_fields = fields


class LayawayPaymentCreateSerializer(serializers.ModelSerializer):
    """Member reports a payment (staff confirms later)."""

    class Meta:
        model = LayawayPayment
        fields = ["amount_rwf", "reference"]
        extra_kwargs = {
            "amount_rwf": {"min_value": 1},
            "reference": {"required": False, "allow_blank": True},
        }

    def validate_amount_rwf(self, value):
        layaway = self.context.get("layaway")
        if not layaway:
            return value
        remaining = layaway.total_rwf - layaway.amount_paid_rwf
        if value > remaining:
            raise serializers.ValidationError(
                f"Amount ({value:,} RWF) exceeds remaining balance ({remaining:,} RWF)."
            )
        return value


class LayawayListSerializer(serializers.ModelSerializer):
    can_cancel_without_penalty = serializers.BooleanField(read_only=True)
    item_images = LayawayImageSerializer(many=True, read_only=True)

    class Meta:
        model = Layaway
        fields = [
            "id",
            "item_description",
            "item_value_rwf",
            "service_fee_rwf",
            "total_rwf",
            "delivery_fee_rwf",
            "status",
            "collection_type",
            "seller_name",
            "seller_phone",
            "seller_address",
            "item_images",
            "start_date",
            "end_date",
            "duration_days",
            "cooling_off_until",
            "amount_paid_rwf",
            "can_cancel_without_penalty",
            "created_at",
        ]
        read_only_fields = fields


class LayawayDetailSerializer(serializers.ModelSerializer):
    can_cancel_without_penalty = serializers.BooleanField(read_only=True)
    item_images = LayawayImageSerializer(many=True, read_only=True)

    class Meta:
        model = Layaway
        fields = [
            "id",
            "item_description",
            "item_value_rwf",
            "service_fee_rwf",
            "total_rwf",
            "delivery_fee_rwf",
            "status",
            "collection_type",
            "seller_name",
            "seller_phone",
            "seller_address",
            "item_images",
            "start_date",
            "end_date",
            "duration_days",
            "confirmed_at",
            "cooling_off_until",
            "amount_paid_rwf",
            "cancellation_penalty_rwf",
            "default_penalty_rwf",
            "can_cancel_without_penalty",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields


class LayawayCreateSerializer(serializers.Serializer):
    item_description = serializers.CharField(
        max_length=300, required=False, allow_blank=True
    )
    item_value_rwf = serializers.IntegerField(min_value=1)
    collection_type = serializers.ChoiceField(
        choices=Layaway.COLLECTION_CHOICES,
        default=Layaway.COLLECTION_PICKUP,
    )
    delivery_fee_rwf = serializers.IntegerField(min_value=0, default=0)
    # Seller info (name optional)
    seller_name = serializers.CharField(
        max_length=150, required=False, allow_blank=True
    )
    seller_phone = serializers.CharField(
        max_length=20, required=False, allow_blank=True
    )
    seller_address = serializers.CharField(
        max_length=300, required=False, allow_blank=True
    )

    def validate_item_value_rwf(self, value):
        if value <= 0:
            raise serializers.ValidationError("Item value must be positive.")
        return value

    def validate(self, attrs):
        user = self.context["request"].user
        eligibility = get_layaway_eligibility(user)
        if not eligibility["can_request"]:
            raise serializers.ValidationError(eligibility["message"])
        item_value = attrs["item_value_rwf"]
        if item_value > eligibility["available_layaway_rwf"]:
            raise serializers.ValidationError(
                f"Item value ({item_value:,} RWF) exceeds your available layaway limit "
                f"({eligibility['available_layaway_rwf']:,} RWF)."
            )
        return attrs


class LayawayEligibilitySerializer(serializers.Serializer):
    has_active_membership = serializers.BooleanField()
    savings_balance_rwf = serializers.IntegerField()
    layaway_limit_rwf = serializers.IntegerField()
    current_layaway_total_rwf = serializers.IntegerField()
    available_layaway_rwf = serializers.IntegerField()
    can_request = serializers.BooleanField()
    message = serializers.CharField()
