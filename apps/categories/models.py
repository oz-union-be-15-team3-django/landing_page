from django.conf import settings
from django.db import models

from apps.transactions.models import Transaction


class Category(models.Model):
    """카테고리 모델"""

    class CategoryType(models.TextChoices):
        INCOME = Transaction.TransactionType.DEPOSIT.value, "수입"
        EXPENSE = Transaction.TransactionType.WITHDRAWAL.value, "지출"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="custom_categories",
        verbose_name="소유자",
    )
    name = models.CharField(max_length=50, verbose_name="카테고리명")
    category_type = models.CharField(
        max_length=10, choices=CategoryType.choices, verbose_name="유형(수입/지출)"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "categories"
        verbose_name = "카테고리"
        verbose_name_plural = "카테고리 목록"
        unique_together = ("user", "name", "category_type")

    def __str__(self):
        return f"[{self.get_category_type_display()}] {self.name} ({self.user.email})"
