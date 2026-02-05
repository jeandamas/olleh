from django.contrib import admin
from .models import User, MemberProfile, MemberMeasurements


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("email", "is_staff", "is_active", "date_joined")
    search_fields = ("email",)


@admin.register(MemberProfile)
class MemberProfileAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "olleh_code",
        "reputation",
        "phone",
        "full_name",
        "district",
        "sector",
    )
    search_fields = (
        "olleh_code",
        "user__email",
        "full_name",
        "phone",
        "district",
        "sector",
    )
    raw_id_fields = ("user",)
    fieldsets = (
        (None, {"fields": ("user", "olleh_code", "reputation")}),
        (
            "Contact",
            {
                "fields": (
                    "full_name",
                    "phone",
                    "alternate_phone",
                    "national_id",
                )
            },
        ),
        (
            "Delivery address",
            {
                "fields": (
                    "district",
                    "sector",
                    "cell",
                    "village",
                    "street",
                    "house_number",
                    "address_notes",
                )
            },
        ),
    )


@admin.register(MemberMeasurements)
class MemberMeasurementsAdmin(admin.ModelAdmin):
    list_display = ("user", "height_cm", "waist_cm", "shoe_size_eu")
    raw_id_fields = ("user",)
