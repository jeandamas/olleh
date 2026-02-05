from django.contrib import admin
from .models import SavingsAccount, SavingsTransaction, RefundRequest


@admin.register(SavingsAccount)
class SavingsAccountAdmin(admin.ModelAdmin):
    list_display = ("user", "balance_rwf", "created_at")
    search_fields = ("user__email",)
    readonly_fields = ("created_at", "updated_at")


@admin.register(SavingsTransaction)
class SavingsTransactionAdmin(admin.ModelAdmin):
    list_display = ("account", "kind", "amount_rwf", "reference", "created_at")
    list_filter = ("kind",)
    search_fields = ("account__user__email", "reference")
    readonly_fields = ("created_at",)


@admin.register(RefundRequest)
class RefundRequestAdmin(admin.ModelAdmin):
    list_display = ("account", "amount_rwf", "status", "created_at")
    list_filter = ("status",)
    search_fields = ("account__user__email",)
    readonly_fields = ("created_at", "updated_at")
    raw_id_fields = ("account",)
