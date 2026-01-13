from django.contrib import admin

from .models import Category


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """카테고리 Admin 설정"""

    list_display = [
        "id",
        "name",
        "category_type",
        "user",
        "created_at",
    ]

    list_filter = [
        "category_type",
        "created_at",
    ]

    search_fields = [
        "name",
        "user__username",
    ]

    readonly_fields = ["created_at"]

    ordering = ["-created_at"]
