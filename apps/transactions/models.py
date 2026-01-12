from django.conf import settings
from django.db import models


class Transaction(models.Model):
    """거래 내역 모델"""

    class TransactionType(models.TextChoices):
        DEPOSIT = "Deposit", "입금"
        WITHDRAWAL = "WITHDRAWAL", "출금"
        TRANSFER = "TRANSFER", "이체"

    class Currency(models.TextChoices):
        KRW = "KRW", "원화(₩)"
        USD = "USD", "달러($)"
        JPY = "JPY", "엔화(¥)"
        EUR = "EUR", "유로(€)"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="transactions",
        verbose_name="사용자",
    )
    account = models.ForeignKey(
        "accounts.Account",
        on_delete=models.SET_NULL,  # 카테고리가 삭제되어도 거래 내역은 남게 SET_NULL로 설정
        null=True,
        blank=True,
        related_name="transactions",
        verbose_name="계좌",
    )
    to_account = models.ForeignKey(
        "accounts.Account",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="incoming_transfers",
        verbose_name="입금 대상 계좌 (이체 시)",
    )
    category = models.ForeignKey(
        "categories.Category",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="transactions",
        verbose_name="카테고리",
    )  # 카테고리id

    transaction_type = models.CharField(
        max_length=10, choices=TransactionType.choices, verbose_name="거래 유형"
    )
    currency = models.CharField(
        max_length=4,
        choices=Currency.choices,
        default=Currency.KRW,
        verbose_name="통화",
    )
    amount = models.DecimalField(
        max_digits=15, decimal_places=2, verbose_name="거래 금액"
    )
    balance_after_transaction = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name="거래 후 잔액",
        help_text="거래 직후의 계좌 잔액 기록",
    )
    description = models.TextField(blank=True, null=True, verbose_name="거래 메모")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="거래 일시")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "transactions"
        ordering = ["-created_at"]
        verbose_name = "거래 내역"
        verbose_name_plural = "거래 내역 목록"

    def __str__(self):
        return f"{self.get_transaction_type_display()} - {self.amount} {self.currency} ({self.account.account_name})"

    # def save(self, *args, **kwargs):
    #     # 새로 생성하는 경우에만 잔액 업데이트
    #     is_new = self.pk is None
    #     if not is_new:
    #         # 수정 시 이전 거래의 영향 제거
    #         old_transaction = Transaction.objects.get(pk=self.pk)
    #         if old_transaction.transaction_type == "deposit":
    #             self.account.balance -= old_transaction.amount
    #         elif old_transaction.transaction_type == "withdrawal":
    #             self.account.balance += old_transaction.amount

    #     super().save(*args, **kwargs)

    #     # 새로 생성하거나 수정된 경우 잔액 업데이트
    #     if self.transaction_type == "deposit":
    #         self.account.balance += self.amount
    #     elif self.transaction_type == "withdrawal":
    #         self.account.balance -= self.amount
    #     self.account.save()

    # def delete(self, *args, **kwargs):
    #     # 거래 삭제 시 계좌 잔액 복구
    #     if self.transaction_type == "deposit":
    #         self.account.balance -= self.amount
    #     elif self.transaction_type == "withdrawal":
    #         self.account.balance += self.amount
    #     self.account.save()
    #     super().delete(*args, **kwargs)
