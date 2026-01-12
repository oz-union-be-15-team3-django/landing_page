from rest_framework import serializers

from .models import Category


class CategoryCreateRequestSerializer(serializers.Serializer):
    """카테고리 생성 요청 스펙"""

    category_name = serializers.CharField(max_length=100, help_text="카테고리명")
    category_type = serializers.ChoiceField(
        choices=["income", "expense"],
        help_text="카테고리유형: income(수입) 또는 expense(지출)",
    )


class CategoryUpdateRequestSerializer(serializers.Serializer):
    """카테고리 수정 요청 스펙"""

    category_name = serializers.CharField(
        max_length=100, required=False, help_text="카테고리명"
    )
    category_type = serializers.ChoiceField(
        choices=["income", "expense"],
        required=False,
        help_text="카테고리유형: income(수입) 또는 expense(지출)",
    )


class CategoryResponseSerializer(serializers.ModelSerializer):
    """카테고리 응답 스펙"""

    category_type_display = serializers.CharField(
        source="get_category_type_display", read_only=True
    )

    class Meta:
        model = Category
        fields = [
            "id",
            "user",
            "category_name",
            "category_type",
            "category_type_display",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "user", "created_at", "updated_at"]
