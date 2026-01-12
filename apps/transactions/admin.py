from django.contrib import admin
from django.db import transaction

from .models import Transaction


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "account",
        "transaction_type",
        "amount",
        "balance_after_transaction",
        "created_at",
    )
    list_filter = ("transaction_type", "created_at")
    search_fields = (
        "user__email",
        "account__account_number",
        "category",
        "description",
    )
    readonly_fields = ("balance_after_transaction", "created_at", "updated_at")
    date_hierarchy = "created_at"

    @transaction.atomic
    def save_model(self, request, obj, form, change):
        """
        어드민 페이지에서 수정/생성 시에도 잔액 로직이 작동하도록 보완
        """
        if change:
            # 수정 시: 기존 데이터 가져오기
            old_obj = Transaction.objects.get(pk=obj.pk)
            # 1. 기존 효과 되돌리기
            self._adjust_balance(old_obj, revert=True)

        # 2. 새로운 효과 적용 및 저장
        self._adjust_balance(obj, revert=False)
        obj.balance_after_transaction = obj.account.balance
        super().save_model(request, obj, form, change)

    @transaction.atomic
    def delete_model(self, request, obj):
        """
        어드민에서 삭제 시 잔액 복구
        """
        self._adjust_balance(obj, revert=True)
        super().delete_model(request, obj)

    def _adjust_balance(self, obj, revert=False):
        """잔액 조정 헬퍼 함수"""
        account = obj.account
        to_account = obj.to_account
        amount = obj.amount
        t_type = obj.transaction_type

        mult = -1 if revert else 1

        if t_type == Transaction.TransactionType.DEPOSIT:
            account.balance += amount * mult
        elif t_type == Transaction.TransactionType.WITHDRAWAL:
            account.balance -= amount * mult
        elif t_type == Transaction.TransactionType.TRANSFER:
            account.balance -= amount * mult
            if to_account:
                to_account.balance += amount * mult
                to_account.save()

        account.save()
