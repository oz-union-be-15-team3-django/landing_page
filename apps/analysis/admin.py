from django.contrib import admin

from .models import SpendingAnalysis


@admin.register(SpendingAnalysis)
class SpendingAnalysisAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "analysis_type",
        "start_date",
        "end_date",
        "total_income",
        "total_expense",
        "net_amount",
        "created_at",
    )
    list_filter = ("analysis_type", "created_at")
    search_fields = ("user__username", "user__email")
    readonly_fields = ("created_at", "updated_at")
    date_hierarchy = "created_at"
