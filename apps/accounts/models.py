from django.conf import settings
from django.db import models

# 사용자id (이 계좌의 주인)
# 계좌명
# 은행명
# 계좌번호마스킹
# 활성여부
# 생성일시
# 수정일시


class Account(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # 유저
    AccountName = models.CharField(max_length=15)  # 카테로리 이름
    BankName = models.CharField(max_length=20)  # 은행이름
    Account_Num_masked = models.CharField(
        max_length=30
    )  # 마스킹 계좌번호 serializer에서 자동 마스킹 예정
    is_active = models.BooleanField(default=True)  # 계좌 활성여부
    CreatedAt = models.DateTimeField(auto_now_add=True)  # 계좌 생성일시
    UpdatedAt = models.DateTimeField(auto_now=True)  # 계좌 수정일시

    def __str__(self):
        return self.AccountName
