from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.savings.views import (
    SavingsBalanceViewSet,
    SavingsDepositViewSet,
    SavingsTransactionViewSet,
    RefundRequestViewSet,
)

router = DefaultRouter()
router.register(r"balance", SavingsBalanceViewSet, basename="savings-balance")
router.register(r"deposit", SavingsDepositViewSet, basename="savings-deposit")
router.register(
    r"transactions", SavingsTransactionViewSet, basename="savings-transactions"
)
router.register(
    r"refund-requests", RefundRequestViewSet, basename="savings-refund-request"
)

urlpatterns = [
    path("", include(router.urls)),
]
