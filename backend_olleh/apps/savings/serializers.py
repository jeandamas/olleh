from rest_framework import serializers

from apps.savings.models import SavingsAccount, SavingsTransaction, RefundRequest


class SavingsBalanceSerializer(serializers.Serializer):
    balance_rwf = serializers.IntegerField(read_only=True)
    currency = serializers.CharField(default="RWF", read_only=True)


class SavingsDepositSerializer(serializers.Serializer):
    amount_rwf = serializers.IntegerField(min_value=1)
    reference = serializers.CharField(max_length=100, required=False, allow_blank=True)

    def validate_amount_rwf(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be positive.")
        return value


class SavingsWithdrawSerializer(serializers.Serializer):
    amount_rwf = serializers.IntegerField(min_value=1)
    reason = serializers.CharField(max_length=200, required=False, allow_blank=True)

    def validate_amount_rwf(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be positive.")
        return value


class SavingsTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SavingsTransaction
        fields = [
            "id",
            "kind",
            "amount_rwf",
            "reference",
            "created_at",
        ]
        read_only_fields = fields


class RefundRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = RefundRequest
        fields = [
            "id",
            "amount_rwf",
            "status",
            "reason",
            "created_at",
        ]
        read_only_fields = ["id", "status", "created_at"]
