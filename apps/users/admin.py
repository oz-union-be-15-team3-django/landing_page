from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = (
        "email",
        "nickname",
        "phone_number",
        "is_staff",
        "is_active",
        "created_at",
    )

    search_fields = ("username", "email", "nickname", "phone_number")

    list_filter = ("is_staff", "is_superuser", "is_active")

    readonly_fields = ("is_staff", "is_superuser")

    fieldsets = UserAdmin.fieldsets + (
        ("추가 정보", {"fields": ("nickname", "phone_number")}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("추가 정보", {"fields": ("nickname", "phone_number")}),
    )


class ActiveUserFilter(admin.SimpleListFilter):
    title = "활성화 상태"
    parameter_name = "activate_status"

    def lookups(self, request, model_admin):
        return [
            ("active", "활성화됨"),
            ("inactive", "비활성화됨"),
        ]

    def queryset(self, request, queryset):
        if self.value() == "active":
            return queryset.filter(is_active=True)
        if self.value() == "inactive":
            return queryset.filter(is_active=False)
        return queryset
