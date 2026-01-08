from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models

from apps.categories.models import Category

# 사용자id
# 계좌id
# 카테고리id
# 거래유형 (INCOME / EXPENSE)
# 금액
# 메모
# 거래일시
# 생성일시
# 수정일시


class Transaction(models.Model):
    TRANSACTION_TYPE_CHOICES = [
        ("deposit", "입금"),
        ("withdrawal", "출금"),
    ]

    account = models.ForeignKey(
        "accounts.Account", on_delete=models.CASCADE, related_name="transactions"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="transactions"
    )  # 사용자id
    transaction_type = models.CharField(
        max_length=10, choices=TRANSACTION_TYPE_CHOICES, default="deposit"
    )
    amount = models.DecimalField(
        max_digits=15, decimal_places=2, validators=[MinValueValidator(Decimal("0.01"))]
    )
    description = models.TextField(blank=True, null=True)
    transaction_date = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    category = models.ForeignKey(Category, on_delete=models.CASCADE)  # 카테고리id

    class Meta:
        db_table = "transactions"
        ordering = ["-transaction_date"]
        indexes = [
            models.Index(fields=["user", "transaction_date"]),
            models.Index(fields=["account", "transaction_date"]),
        ]

    def __str__(self):
        return f"{self.get_transaction_type_display()} - {self.amount} ({self.account.account_name})"

    def save(self, *args, **kwargs):
        # 새로 생성하는 경우에만 잔액 업데이트
        is_new = self.pk is None
        if not is_new:
            # 수정 시 이전 거래의 영향 제거
            old_transaction = Transaction.objects.get(pk=self.pk)
            if old_transaction.transaction_type == "deposit":
                self.account.balance -= old_transaction.amount
            elif old_transaction.transaction_type == "withdrawal":
                self.account.balance += old_transaction.amount

        super().save(*args, **kwargs)

        # 새로 생성하거나 수정된 경우 잔액 업데이트
        if self.transaction_type == "deposit":
            self.account.balance += self.amount
        elif self.transaction_type == "withdrawal":
            self.account.balance -= self.amount
        self.account.save()

    def delete(self, *args, **kwargs):
        # 거래 삭제 시 계좌 잔액 복구
        if self.transaction_type == "deposit":
            self.account.balance -= self.amount
        elif self.transaction_type == "withdrawal":
            self.account.balance += self.amount
        self.account.save()
        super().delete(*args, **kwargs)
