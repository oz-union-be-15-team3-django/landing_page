from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Category

User = get_user_model()


@receiver(post_save, sender=User)
def create_default_categories(sender, instance, created, **kwargs):
    """새로운 유저가 생성될 때 기본 카테고리를 자동으로 생성합니다."""

    if created:
        # 1. 수입 카테고리
        income_categories = ["월급", "상여", "부수입", "금융소득", "용돈", "기타"]

        # 2. 지출 카테고리
        expense_categories = [
            "식비",
            "교통비",
            "문화생활",
            "생활용품",
            "주거/통신",
            "패션/미용",
            "헬스케어",
            "교육",
            "기타",
        ]

        categories_to_create = []

        # 수입 카테고리 객체 생성 준비
        for name in income_categories:
            categories_to_create.append(
                Category(
                    user=instance,
                    name=name,
                    category_type=Category.CategoryType.INCOME,
                )
            )

        # 지출 카테고리 객체 생성 준비
        for name in expense_categories:
            categories_to_create.append(
                Category(
                    user=instance,
                    name=name,
                    category_type=Category.CategoryType.EXPENSE,
                )
            )

        # 데이터베이스에 한꺼번에 저장 (성능 최적화)
        Category.objects.bulk_create(categories_to_create)
