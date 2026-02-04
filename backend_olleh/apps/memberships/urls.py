from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.memberships.views import MembershipViewSet, UserMembershipViewSet

app_name = "memberships"

# Create a router and register our viewsets
router = DefaultRouter()
router.register(r"memberships", MembershipViewSet, basename="membership")
router.register(r"user-memberships", UserMembershipViewSet, basename="user-membership")

urlpatterns = [
    path("", include(router.urls)),
]
