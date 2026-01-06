from django.db import models
from django.conf import settings
# 사용자 id
# 카테고리명
# 카테고리 유형
# 생성일시
# 수정일시

# 카테고리 타입 입금 출금
CATEGORY_TYPE_CHOICES = [
    ("INCOME", "INCOME"),
    ("EXPENSE", "EXPENSE"),
]

class Category(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE) # 유저
    CategoryName = models.CharField(max_length=100) # 카테로리 이름
    CategoryType = models.CharField(max_length=10, choices=CATEGORY_TYPE_CHOICES) # 카테고리 유형
    CreatedAt = models.DateTimeField(auto_now_add=True) # 생성일시
    UpdatedAt = models.DateTimeField(auto_now=True) # 수정일시
    
    # Admin 에서 객체표시
    def __str__(self):
        return self.CategoryName