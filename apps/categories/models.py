from django.conf import settings
from django.db import models


class Category(models.Model):
    """
    카테고리 모델

    ERD 기반:
    - id: Primary Key (자동 생성)
    - user: Foreign Key (User) - 사용자Id
    - category_name: 카테고리명
    - category_type: 카테고리유형 (income: 수입, expense: 지출)
    - created_at: 생성일시
    - updated_at: 수정일시
    """

    CATEGORY_TYPE_CHOICES = [
        ("income", "수입"),
        ("expense", "지출"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="categories",
        verbose_name="사용자",
    )
    category_name = models.CharField(max_length=100, verbose_name="카테고리명")
    category_type = models.CharField(
        max_length=10, choices=CATEGORY_TYPE_CHOICES, verbose_name="카테고리유형"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="생성일시")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="수정일시")

    class Meta:
        db_table = "categories"
        verbose_name = "카테고리"
        verbose_name_plural = "카테고리"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "category_type"]),
        ]

    def __str__(self):
        return f"{self.category_name} ({self.get_category_type_display()})"
