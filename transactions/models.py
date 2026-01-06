from django.db import models
from django.conf import settings
from accounts.models import Account
from categories.models import Category
# 사용자id
# 계좌id
# 카테고리id
# 거래유형 (INCOME / EXPENSE)
# 금액
# 메모
# 거래일시
# 생성일시
# 수정일시

#거래 유형
TRANSACTION_TYPE_CHOICES = [
    ("INCOME", "INCOME"),
    ("EXPENSE", "EXPENSE"),
]


class Transaction(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE) # 사용자id
    account = models.ForeignKey(Account, on_delete=models.CASCADE) # 계좌id
    category = models.ForeignKey(Category, on_delete=models.CASCADE) # 카테고리id
    TransactionType = models.CharField(max_length=10, choices=TRANSACTION_TYPE_CHOICES) # 거래유형
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    memo = models.TextField(blank=True)
    transaction_date = models.DateTimeField()
    CreatedAt = models.DateTimeField(auto_now_add=True) # 생성일시
    UpdatedAt = models.DateTimeField(auto_now=True) # 수정일시

    def __str__(self):
        return f"{self.transaction_date} - {self.amount}"