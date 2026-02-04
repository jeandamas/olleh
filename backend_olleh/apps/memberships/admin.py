from django.contrib import admin
from django.utils.html import format_html
from django.contrib import messages
from .models import Membership, UserMembership


# --- Membership Admin ---


@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "price",
        "max_order_price",
        "duration_days",
        "is_available",
        "created_at",
    )
    list_filter = ("is_available",)
    search_fields = ("name", "description")
    ordering = ("price",)
    readonly_fields = ("id", "created_at", "updated_at")
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "id",
                    "name",
                    "description",
                    "price",
                    "max_order_price",
                    "duration_days",
                    "is_available",
                )
            },
        ),
        (
            "Timestamps",
            {
                "fields": ("created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
    )


# --- UserMembership Admin ---


@admin.register(UserMembership)
class UserMembershipAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user_email",
        "membership_name",
        "status_badge",
        "payment_mode",
        "amount_paid",
        "start_date",
        "end_date",
        "is_active_badge",
        "created_at",
    )
    list_filter = ("status", "payment_mode", "membership", "created_at")
    search_fields = ("user__email", "membership__name", "payment_reference")
    readonly_fields = (
        "id",
        "is_active",
        "created_at",
        "updated_at",
        "payment_confirmed_by",
        "payment_confirmed_at",
    )
    ordering = ("-created_at",)
    actions = ["mark_as_paid", "activate_membership", "cancel_membership"]

    fieldsets = (
        (
            "Basic Information",
            {
                "fields": (
                    "id",
                    "user",
                    "membership",
                    "status",
                )
            },
        ),
        (
            "Payment Information",
            {
                "fields": (
                    "payment_mode",
                    "payment_reference",
                    "amount_paid",
                    "payment_confirmed_by",
                    "payment_confirmed_at",
                )
            },
        ),
        (
            "Membership Period",
            {
                "fields": (
                    "start_date",
                    "end_date",
                    "is_active",
                )
            },
        ),
        (
            "Timestamps",
            {
                "fields": ("created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
    )

    def user_email(self, obj):
        return obj.user.email

    user_email.short_description = "User Email"
    user_email.admin_order_field = "user__email"

    def membership_name(self, obj):
        return obj.membership.name

    membership_name.short_description = "Membership"
    membership_name.admin_order_field = "membership__name"

    def status_badge(self, obj):
        colors = {
            "pending": "#FFA500",  # Orange
            "paid": "#0066CC",  # Blue
            "active": "#28A745",  # Green
            "expired": "#6C757D",  # Gray
            "canceled": "#DC3545",  # Red
        }
        color = colors.get(obj.status, "#000000")
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display(),
        )

    status_badge.short_description = "Status"
    status_badge.admin_order_field = "status"

    def is_active_badge(self, obj):
        if obj.is_active:
            return format_html(
                '<span style="color: green; font-weight: bold;">✓ Active</span>'
            )
        return format_html('<span style="color: gray;">✗ Inactive</span>')

    is_active_badge.short_description = "Active"

    def mark_as_paid(self, request, queryset):
        """Admin action to mark memberships as paid"""
        count = 0
        errors = 0

        for membership in queryset:
            try:
                membership.mark_as_paid(request.user)
                count += 1
            except Exception as e:
                errors += 1
                messages.error(
                    request, f"Error marking {membership.user.email} as paid: {str(e)}"
                )

        if count > 0:
            messages.success(
                request, f"Successfully marked {count} membership(s) as paid."
            )
        if errors > 0:
            messages.warning(request, f"Failed to mark {errors} membership(s) as paid.")

    mark_as_paid.short_description = "Mark selected as PAID"

    def activate_membership(self, request, queryset):
        """Admin action to activate memberships"""
        count = 0
        errors = 0

        for membership in queryset:
            try:
                membership.activate(request.user)
                count += 1
            except Exception as e:
                errors += 1
                messages.error(
                    request,
                    f"Error activating membership for {membership.user.email}: {str(e)}",
                )

        if count > 0:
            messages.success(request, f"Successfully activated {count} membership(s).")
        if errors > 0:
            messages.warning(request, f"Failed to activate {errors} membership(s).")

    activate_membership.short_description = "Activate selected memberships"

    def cancel_membership(self, request, queryset):
        """Admin action to cancel memberships"""
        count = 0
        errors = 0

        for membership in queryset:
            try:
                membership.cancel()
                count += 1
            except Exception as e:
                errors += 1
                messages.error(
                    request,
                    f"Error canceling membership for {membership.user.email}: {str(e)}",
                )

        if count > 0:
            messages.success(request, f"Successfully canceled {count} membership(s).")
        if errors > 0:
            messages.warning(request, f"Failed to cancel {errors} membership(s).")

    cancel_membership.short_description = "Cancel selected memberships"

    def save_model(self, request, obj, form, change):
        """
        Ensure the 'one active membership' rule is enforced in the admin as well.
        """
        super().save_model(request, obj, form, change)
