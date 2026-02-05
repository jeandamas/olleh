from rest_framework import serializers

from apps.orders.models import (
    Layaway,
    compute_service_fee_rwf,
    LAYAWAY_MIN_DAYS,
    LAYAWAY_MAX_DAYS,
)
from apps.orders.services import get_layaway_eligibility


class LayawayListSerializer(serializers.ModelSerializer):
    can_cancel_without_penalty = serializers.BooleanField(read_only=True)

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
    item_description = serializers.CharField(max_length=300, required=False, allow_blank=True)
    item_value_rwf = serializers.IntegerField(min_value=1)
    collection_type = serializers.ChoiceField(
        choices=Layaway.COLLECTION_CHOICES,
        default=Layaway.COLLECTION_PICKUP,
    )
    delivery_fee_rwf = serializers.IntegerField(min_value=0, default=0)

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
