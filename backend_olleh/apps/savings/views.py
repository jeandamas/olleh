from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from drf_spectacular.utils import extend_schema

from apps.savings.models import SavingsAccount, RefundRequest, SavingsTransaction
from apps.savings.serializers import (
    SavingsBalanceSerializer,
    SavingsDepositSerializer,
    SavingsTransactionSerializer,
    RefundRequestSerializer,
)
from apps.memberships.permissions import IsAuthenticatedClient


class SavingsBalanceViewSet(GenericViewSet):
    """Simple balance + deposit + transactions + refund request."""

    permission_classes = [IsAuthenticatedClient]

    def get_account(self):
        return SavingsAccount.get_or_create_for_user(self.request.user)

    @extend_schema(
        summary="Get my savings balance",
        description="Returns current savings balance in RWF.",
        tags=["Client - Savings"],
        responses={200: SavingsBalanceSerializer},
    )
    def list(self, request):
        account = self.get_account()
        return Response(
            SavingsBalanceSerializer({"balance_rwf": account.balance_rwf}).data
        )


class SavingsDepositViewSet(GenericViewSet):
    permission_classes = [IsAuthenticatedClient]

    def get_account(self):
        return SavingsAccount.get_or_create_for_user(self.request.user)

    @extend_schema(
        summary="Deposit to savings",
        request=SavingsDepositSerializer,
        tags=["Client - Savings"],
        responses={200: SavingsBalanceSerializer, 400: None},
    )
    def create(self, request):
        serializer = SavingsDepositSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        account = self.get_account()
        try:
            account.credit(
                amount_rwf=serializer.validated_data["amount_rwf"],
                transaction_type=SavingsTransaction.KIND_DEPOSIT,
                reference=serializer.validated_data.get("reference", ""),
            )
        except Exception as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(
            SavingsBalanceSerializer({"balance_rwf": account.balance_rwf}).data,
            status=status.HTTP_200_OK,
        )


class SavingsTransactionViewSet(GenericViewSet):
    permission_classes = [IsAuthenticatedClient]

    @extend_schema(
        summary="List savings transactions",
        tags=["Client - Savings"],
        responses={200: SavingsTransactionSerializer(many=True)},
    )
    def list(self, request):
        account = SavingsAccount.get_or_create_for_user(request.user)
        qs = account.transactions.all()[:100]
        serializer = SavingsTransactionSerializer(qs, many=True)
        return Response(serializer.data)


class RefundRequestViewSet(GenericViewSet):
    permission_classes = [IsAuthenticatedClient]

    @extend_schema(
        summary="Request savings refund",
        description="Request withdrawal of savings. Processed within 7 working days per OLLEH policy.",
        request=RefundRequestSerializer,
        tags=["Client - Savings"],
        responses={201: RefundRequestSerializer, 400: None},
    )
    def create(self, request):
        serializer = RefundRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        account = SavingsAccount.get_or_create_for_user(request.user)
        amount = serializer.validated_data["amount_rwf"]
        if amount > account.balance_rwf:
            return Response(
                {"detail": "Insufficient balance for this refund request."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        refund = RefundRequest.objects.create(
            account=account,
            amount_rwf=amount,
            reason=serializer.validated_data.get("reason", ""),
        )
        return Response(
            RefundRequestSerializer(refund).data,
            status=status.HTTP_201_CREATED,
        )

    @extend_schema(
        summary="List my refund requests",
        tags=["Client - Savings"],
        responses={200: RefundRequestSerializer(many=True)},
    )
    def list(self, request):
        account = SavingsAccount.get_or_create_for_user(request.user)
        qs = account.refund_requests.all()
        return Response(RefundRequestSerializer(qs, many=True).data)
