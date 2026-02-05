from django.contrib import admin, messages
from .models import Layaway, LayawayImage
from apps.payments.models import LayawayPayment


class LayawayImageInline(admin.TabularInline):
    model = LayawayImage
    extra = 0
    fields = ("image", "caption", "order")


class LayawayPaymentInline(admin.TabularInline):
    model = LayawayPayment
    extra = 0
    fields = ("amount_rwf", "reference", "created_at", "confirmed_at", "confirmed_by")
    readonly_fields = ("created_at",)
    raw_id_fields = ("confirmed_by",)


@admin.register(Layaway)
class LayawayAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "item_value_rwf",
        "total_rwf",
        "status",
        "collection_type",
        "seller_phone",
        "created_at",
    )
    list_filter = ("status", "collection_type")
    search_fields = (
        "user__email",
        "item_description",
        "seller_name",
        "seller_phone",
    )
    raw_id_fields = ("user",)
    readonly_fields = ("created_at", "updated_at", "confirmed_at", "cooling_off_until")
    inlines = [LayawayImageInline, LayawayPaymentInline]
    actions = ["confirm_layaways", "activate_layaways"]

    @admin.action(description="Confirm selected (start cooling-off)")
    def confirm_layaways(self, request, queryset):
        for obj in queryset:
            try:
                obj.confirm_by_olleh()
            except Exception as e:
                self.message_user(
                    request, f"Layaway {obj.id}: {e}", level=messages.ERROR
                )
        self.message_user(request, "Selected layaways confirmed.")

    @admin.action(description="Activate selected (14–30 days)")
    def activate_layaways(self, request, queryset):
        for obj in queryset:
            try:
                obj.activate()
            except Exception as e:
                self.message_user(
                    request, f"Layaway {obj.id}: {e}", level=messages.ERROR
                )
        self.message_user(request, "Selected layaways activated.")
