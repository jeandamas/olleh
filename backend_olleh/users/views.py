from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from drf_spectacular.utils import extend_schema

from users.models import MemberProfile, MemberMeasurements
from users.serializers import MemberProfileSerializer, MemberMeasurementsSerializer
from apps.memberships.permissions import IsAuthenticatedClient


class MemberProfileViewSet(GenericViewSet):
    permission_classes = [IsAuthenticatedClient]

    @extend_schema(
        summary="Get my OLLEH profile",
        description="Returns member profile including OLLEH code and reputation.",
        tags=["Client - Profile"],
        responses={200: MemberProfileSerializer},
    )
    def list(self, request):
        profile, _ = MemberProfile.objects.get_or_create(
            user=request.user,
            defaults={},
        )
        return Response(MemberProfileSerializer(profile).data)

    @extend_schema(
        summary="Update my profile",
        description="Update full name, phone, national ID. OLLEH code and reputation are read-only.",
        tags=["Client - Profile"],
        request=MemberProfileSerializer,
        responses={200: MemberProfileSerializer},
    )
    def partial_update(self, request):
        profile, _ = MemberProfile.objects.get_or_create(
            user=request.user,
            defaults={},
        )
        serializer = MemberProfileSerializer(
            profile,
            data=request.data,
            partial=True,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class MemberMeasurementsViewSet(GenericViewSet):
    permission_classes = [IsAuthenticatedClient]

    @extend_schema(
        summary="Get my measurements",
        description="Optional body and shoe measurements for fit assistance.",
        tags=["Client - Profile"],
        responses={200: MemberMeasurementsSerializer},
    )
    def list(self, request):
        try:
            measurements = request.user.measurements
        except MemberMeasurements.DoesNotExist:
            return Response(
                MemberMeasurementsSerializer(
                    MemberMeasurements(user=request.user)
                ).data,
                status=status.HTTP_200_OK,
            )
        return Response(MemberMeasurementsSerializer(measurements).data)

    @extend_schema(
        summary="Create or update my measurements",
        description="Set body and shoe measurements. Provided as assistance only, not guarantees.",
        tags=["Client - Profile"],
        request=MemberMeasurementsSerializer,
        responses={200: MemberMeasurementsSerializer},
    )
    def create(self, request):
        measurements, created = MemberMeasurements.objects.get_or_create(
            user=request.user,
            defaults={},
        )
        serializer = MemberMeasurementsSerializer(
            measurements,
            data=request.data,
            partial=True,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
