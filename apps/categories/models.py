from django.conf import settings
from django.db import models

# 사용자 id
# 카테고리명
# 카테고리 유형
# 생성일시
# 수정일시

# 카테고리 타입 입금 출금
CATEGORY_TYPE_CHOICES = [
    ("INCOME1", "월급"),
    ("INCOME2", "용돈"),
    ("EXPENSE", "지출"),
]


class Category(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # 유저
    category_name = models.CharField(max_length=100)  # 카테고리 이름
    category_type = models.CharField(
        max_length=10, choices=CATEGORY_TYPE_CHOICES
    )  # 카테고리 유형
    created_at = models.DateTimeField(auto_now_add=True)  # 생성일시
    updated_at = models.DateTimeField(auto_now=True)  # 수정일시

    # Admin 에서 객체표시
    def __str__(self):
        return self.CategoryName
