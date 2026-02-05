from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view

from apps.memberships.models import Membership, UserMembership
from apps.memberships.serializers import (
    MembershipSerializer,
    UserMembershipListSerializer,
    UserMembershipDetailSerializer,
    UserMembershipCreateSerializer,
    UserMembershipUpdateSerializer,
)
from apps.memberships.permissions import IsOwnerOrAdmin, IsAuthenticatedClient


# =========================
# Membership ViewSet (Available Tiers)
# =========================


@extend_schema_view(
    list=extend_schema(
        summary="List available membership tiers",
        description="Get a list of all available membership tiers that users can subscribe to.",
        tags=["Client - Memberships"],
    ),
    retrieve=extend_schema(
        summary="Get membership tier details",
        description="Get detailed information about a specific membership tier.",
        tags=["Client - Memberships"],
    ),
)
class MembershipViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing available membership tiers.
    Clients can view all available membership options.
    """

    queryset = Membership.objects.filter(is_available=True).order_by("price")
    serializer_class = MembershipSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ["price", "duration_days", "created_at"]
    ordering = ["price"]


# =========================
# User Membership ViewSet
# =========================


@extend_schema_view(
    list=extend_schema(
        summary="List user's membership requests",
        description="Get a list of all membership requests made by the authenticated user.",
        tags=["Client - User Memberships"],
    ),
    retrieve=extend_schema(
        summary="Get membership request details",
        description="Get detailed information about a specific membership request.",
        tags=["Client - User Memberships"],
    ),
    create=extend_schema(
        summary="Request a new membership",
        description="Create a new membership request. The user must provide payment information.",
        tags=["Client - User Memberships"],
    ),
    partial_update=extend_schema(
        summary="Update payment information",
        description="Update payment information for a pending membership request.",
        tags=["Client - User Memberships"],
    ),
    destroy=extend_schema(
        summary="Cancel membership request",
        description="Cancel a pending or paid membership request.",
        tags=["Client - User Memberships"],
    ),
)
class UserMembershipViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing user membership requests.

    Clients can:
    - View their own membership requests
    - Create new membership requests
    - Update payment information for pending requests
    - Cancel pending/paid requests
    """

    permission_classes = [IsAuthenticatedClient, IsOwnerOrAdmin]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["status", "membership"]
    ordering_fields = ["created_at", "start_date", "end_date"]
    ordering = ["-created_at"]

    def get_queryset(self):
        """
        Users can only see their own memberships.
        Admins can see all memberships.
        """
        user = self.request.user
        if user.is_staff or user.is_superuser:
            return UserMembership.objects.all()
        return UserMembership.objects.filter(user=user)

    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == "create":
            return UserMembershipCreateSerializer
        elif self.action in ["update", "partial_update"]:
            return UserMembershipUpdateSerializer
        elif self.action == "list":
            return UserMembershipListSerializer
        return UserMembershipDetailSerializer

    def perform_create(self, serializer):
        """Create a new membership request for the authenticated user"""
        serializer.save(user=self.request.user)

    def destroy(self, request, *args, **kwargs):
        """Cancel a membership request"""
        instance = self.get_object()

        try:
            instance.cancel()
            return Response(
                {"detail": "Membership request canceled successfully."},
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

    @extend_schema(
        summary="Get active membership",
        description="Get the user's currently active membership if any.",
        tags=["Client - User Memberships"],
        responses={200: UserMembershipDetailSerializer, 404: None},
    )
    @action(detail=False, methods=["get"])
    def active(self, request):
        """Get the user's currently active (non-expired) membership (at most one per user)."""
        active_membership = UserMembership.get_active_for_user(request.user)
        if not active_membership:
            return Response(
                {"detail": "No active membership found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = UserMembershipDetailSerializer(active_membership)
        return Response(serializer.data)

    @extend_schema(
        summary="Get pending memberships",
        description="Get all pending membership requests for the authenticated user.",
        tags=["Client - User Memberships"],
        responses={200: UserMembershipListSerializer(many=True)},
    )
    @action(detail=False, methods=["get"])
    def pending(self, request):
        """Get all pending membership requests"""
        pending_memberships = self.get_queryset().filter(
            status=UserMembership.STATUS_PENDING
        )
        serializer = UserMembershipListSerializer(pending_memberships, many=True)
        return Response(serializer.data)

    @extend_schema(
        summary="Get membership history",
        description="Get all expired and canceled memberships for the authenticated user.",
        tags=["Client - User Memberships"],
        responses={200: UserMembershipListSerializer(many=True)},
    )
    @action(detail=False, methods=["get"])
    def history(self, request):
        """Get membership history (expired and canceled)"""
        history = self.get_queryset().filter(
            status__in=[UserMembership.STATUS_EXPIRED, UserMembership.STATUS_CANCELED]
        )
        serializer = UserMembershipListSerializer(history, many=True)
        return Response(serializer.data)
