from django.contrib import admin
from .models import Payment, LayawayPayment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ["id", "user", "amount", "reference", "status", "created_at"]
    list_filter = ["status"]
    search_fields = ["user__email", "reference"]
    raw_id_fields = ["user", "membership"]


@admin.register(LayawayPayment)
class LayawayPaymentAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "layaway",
        "amount_rwf",
        "reference",
        "created_at",
        "confirmed_at",
        "confirmed_by",
        "is_confirmed",
    ]
    list_filter = ["confirmed_at"]
    search_fields = ["layaway__id", "reference"]
    raw_id_fields = ["layaway", "confirmed_by"]
    readonly_fields = ["created_at", "confirmed_at"]
