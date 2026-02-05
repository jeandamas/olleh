from django.contrib import admin
from .models import User, MemberProfile, MemberMeasurements


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("email", "is_staff", "is_active", "date_joined")
    search_fields = ("email",)


@admin.register(MemberProfile)
class MemberProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "olleh_code", "reputation", "phone", "full_name")
    search_fields = ("olleh_code", "user__email", "full_name")
    raw_id_fields = ("user",)


@admin.register(MemberMeasurements)
class MemberMeasurementsAdmin(admin.ModelAdmin):
    list_display = ("user", "height_cm", "waist_cm", "shoe_size_eu")
    raw_id_fields = ("user",)
