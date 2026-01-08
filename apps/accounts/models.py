from django.conf import settings
from django.db import models

# 사용자id (이 계좌의 주인)
# 계좌명
# 계좌번호
# 은행명
# 계좌번호마스킹
# 활성여부
# 생성일시
# 수정일시


class Account(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="accounts"
    )  # 유저
    account_name = models.CharField(
        max_length=50, unique=True, default="기본 계좌"
    )  # 계좌이름
    account_number = models.CharField(max_length=100)  # 계좌번호
    bank_name = models.CharField(max_length=50)  # 은행이름
    balance = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    is_active = models.BooleanField(default=True, db_index=True)  # 계좌 활성여부
    created_at = models.DateTimeField(auto_now_add=True)  # 계좌 생성일시
    updated_at = models.DateTimeField(auto_now=True)  # 계좌 수정일시
    account_num_masked = models.CharField(
        max_length=100, default=""
    )  # 마스킹 계좌번호 serializer에서 자동 마스킹 예정

    class Meta:
        db_table = "accounts"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.bank_name} - {self.account_name} ({self.account_number})"
