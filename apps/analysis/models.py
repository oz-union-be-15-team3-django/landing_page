from decimal import Decimal

from django.conf import settings
from django.db import models


class SpendingAnalysis(models.Model):
    """소비 분석 데이터 모델"""

    ANALYSIS_TYPE_CHOICES = [
        ("weekly", "주간"),
        ("monthly", "월간"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="spending_analyses",
    )
    analysis_type = models.CharField(max_length=10, choices=ANALYSIS_TYPE_CHOICES)
    start_date = models.DateField()
    end_date = models.DateField()
    total_income = models.DecimalField(
        max_digits=15, decimal_places=2, default=Decimal("0.00")
    )
    total_expense = models.DecimalField(
        max_digits=15, decimal_places=2, default=Decimal("0.00")
    )
    net_amount = models.DecimalField(
        max_digits=15, decimal_places=2, default=Decimal("0.00")
    )
    transaction_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "spending_analyses"
        ordering = ["-start_date"]
        indexes = [
            models.Index(fields=["user", "analysis_type", "start_date"]),
        ]
        unique_together = [["user", "analysis_type", "start_date"]]

    def __str__(self):
        return f"{self.user.username} - {self.get_analysis_type_display()} ({self.start_date} ~ {self.end_date})"
