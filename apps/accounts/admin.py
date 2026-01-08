from django.contrib import admin

from .models import Account


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = (
        "account_number",
        "account_name",
        "bank_name",
        "user",
        "balance",
        "created_at",
    )
    list_filter = ("bank_name", "created_at")
    search_fields = ("account_number", "account_name", "user__email")
    readonly_fields = ("created_at", "updated_at")
