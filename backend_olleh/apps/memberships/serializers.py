from rest_framework import serializers
from django.db import IntegrityError
from django.core.exceptions import ValidationError as DjangoValidationError

from apps.memberships.models import Membership, UserMembership


# =========================
# Membership Serializers
# =========================


class MembershipSerializer(serializers.ModelSerializer):
    """Serializer for available membership tiers"""

    class Meta:
        model = Membership
        fields = [
            "id",
            "name",
            "price",
            "max_order_price",
            "description",
            "duration_days",
            "is_available",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


# =========================
# User Membership Serializers
# =========================


class UserMembershipListSerializer(serializers.ModelSerializer):
    """Serializer for listing user memberships"""

    membership_name = serializers.CharField(source="membership.name", read_only=True)
    membership_price = serializers.IntegerField(
        source="membership.price",
        read_only=True,
    )
    user_email = serializers.EmailField(source="user.email", read_only=True)
    is_active = serializers.BooleanField(read_only=True)

    class Meta:
        model = UserMembership
        fields = [
            "id",
            "user",
            "user_email",
            "membership",
            "membership_name",
            "membership_price",
            "status",
            "start_date",
            "end_date",
            "payment_mode",
            "payment_reference",
            "amount_paid",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "status",
            "start_date",
            "end_date",
            "is_active",
            "created_at",
            "updated_at",
        ]


class UserMembershipDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for user membership"""

    membership_details = MembershipSerializer(source="membership", read_only=True)
    user_email = serializers.EmailField(source="user.email", read_only=True)
    confirmed_by_email = serializers.EmailField(
        source="payment_confirmed_by.email", read_only=True
    )
    is_active = serializers.BooleanField(read_only=True)

    class Meta:
        model = UserMembership
        fields = [
            "id",
            "user",
            "user_email",
            "membership",
            "membership_details",
            "status",
            "start_date",
            "end_date",
            "payment_mode",
            "payment_reference",
            "amount_paid",
            "payment_confirmed_by",
            "confirmed_by_email",
            "payment_confirmed_at",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "user",
            "user_email",
            "status",
            "start_date",
            "end_date",
            "payment_confirmed_by",
            "confirmed_by_email",
            "payment_confirmed_at",
            "is_active",
            "created_at",
            "updated_at",
        ]


class UserMembershipCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating a new membership request"""

    class Meta:
        model = UserMembership
        fields = [
            "membership",
            "payment_mode",
            "payment_reference",
            "amount_paid",
        ]

    def validate_membership(self, value):
        """Ensure the membership tier is available"""
        if not value.is_available:
            raise serializers.ValidationError(
                "This membership tier is not currently available."
            )
        return value

    def validate(self, attrs):
        """Validate payment information"""
        payment_mode = attrs.get("payment_mode")
        payment_reference = attrs.get("payment_reference")
        amount_paid = attrs.get("amount_paid")

        # Payment mode is required
        if not payment_mode:
            raise serializers.ValidationError(
                {"payment_mode": "Payment mode is required."}
            )

        # Payment reference is required for mobile money and bank
        if (
            payment_mode
            in [
                UserMembership.PAYMENT_MOBILE_MONEY,
                UserMembership.PAYMENT_BANK,
            ]
            and not payment_reference
        ):
            raise serializers.ValidationError(
                {
                    "payment_reference": "Payment reference is required for Mobile Money and Bank payments."
                }
            )

        # Amount paid is required
        if not amount_paid:
            raise serializers.ValidationError(
                {"amount_paid": "Amount paid is required."}
            )

        # Validate amount paid matches membership price
        membership = attrs.get("membership")
        if amount_paid != membership.price:
            raise serializers.ValidationError(
                {
                    "amount_paid": f"Amount paid must match the membership price of {membership.price:,} RWF."
                }
            )

        return attrs

    def create(self, validated_data):
        """Create a new membership request"""
        # Set the user from the request context
        user = self.context["request"].user
        membership = validated_data["membership"]
        validated_data["user"] = user
        validated_data["status"] = UserMembership.STATUS_PENDING

        # Check if user already has a pending membership for this tier
        existing_pending = UserMembership.objects.filter(
            user=user,
            membership=membership,
            status=UserMembership.STATUS_PENDING,
        ).first()

        if existing_pending:
            raise serializers.ValidationError(
                {
                    "membership": f"You already have a pending membership request for {membership.name}. "
                    f"Please wait for admin approval or cancel the existing request before creating a new one."
                }
            )

        try:
            return super().create(validated_data)
        except (IntegrityError, DjangoValidationError) as e:
            # Handle database constraint violations
            if "unique_pending_membership" in str(e):
                raise serializers.ValidationError(
                    {
                        "membership": f"You already have a pending membership request for {membership.name}. "
                        f"Please wait for admin approval or cancel the existing request before creating a new one."
                    }
                )
            # Re-raise other validation errors
            raise serializers.ValidationError(
                {
                    "non_field_errors": [
                        "Unable to create membership request. Please try again."
                    ]
                }
            )


class UserMembershipUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating payment information (only for pending memberships)"""

    class Meta:
        model = UserMembership
        fields = [
            "payment_mode",
            "payment_reference",
            "amount_paid",
        ]

    def validate(self, attrs):
        """Validate that only pending memberships can be updated"""
        if self.instance.status != UserMembership.STATUS_PENDING:
            raise serializers.ValidationError(
                "Only pending memberships can be updated."
            )

        # Validate payment reference for specific payment modes
        payment_mode = attrs.get("payment_mode", self.instance.payment_mode)
        payment_reference = attrs.get("payment_reference")

        if (
            payment_mode
            in [
                UserMembership.PAYMENT_MOBILE_MONEY,
                UserMembership.PAYMENT_BANK,
            ]
            and not payment_reference
        ):
            raise serializers.ValidationError(
                {
                    "payment_reference": "Payment reference is required for Mobile Money and Bank payments."
                }
            )

        # Validate amount paid matches membership price if provided
        amount_paid = attrs.get("amount_paid")
        if amount_paid and amount_paid != self.instance.membership.price:
            raise serializers.ValidationError(
                {
                    "amount_paid": f"Amount paid must match the membership price of {self.instance.membership.price:,} RWF."
                }
            )

        return attrs
