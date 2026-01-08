from django.contrib import admin

from .models import Transaction


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "account",
        "transaction_type",
        "amount",
        "transaction_date",
    )
    list_filter = ("transaction_type", "transaction_date")
    search_fields = ("user__email", "account__account_number", "description")
    readonly_fields = ("transaction_date", "updated_at")
    date_hierarchy = "transaction_date"
