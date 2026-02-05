from rest_framework import serializers

from users.models import MemberProfile, MemberMeasurements


class MemberProfileSerializer(serializers.ModelSerializer):
    olleh_code = serializers.CharField(read_only=True)
    reputation = serializers.CharField(read_only=True)

    class Meta:
        model = MemberProfile
        fields = [
            "olleh_code",
            "reputation",
            "full_name",
            "phone",
            "alternate_phone",
            "national_id",
            "district",
            "sector",
            "cell",
            "village",
            "street",
            "house_number",
            "address_notes",
        ]
        read_only_fields = ["olleh_code", "reputation"]


class MemberMeasurementsSerializer(serializers.ModelSerializer):
    class Meta:
        model = MemberMeasurements
        fields = [
            "height_cm",
            "chest_cm",
            "waist_cm",
            "hip_cm",
            "shoe_size_eu",
            "notes",
        ]
