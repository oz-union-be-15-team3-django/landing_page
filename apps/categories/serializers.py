from rest_framework import serializers

from .models import Category


class CategorySerializer(serializers.ModelSerializer):
    """카테고리 시리얼라이저"""

    class Meta:
        model = Category
        fields = ("id", "user", "name", "category_type", "created_at")
        read_only_fields = ("id", "user", "created_at")

    def validate(self, data):
        user = self.context["request"].user
        name = data.get("name")
        c_type = data.get("category_type")

        # 해당 유저가 같은 타입(수입/지출) 내에서 중복된 이름을 쓰는지 체크
        queryset = Category.objects.filter(user=user, name=name, category_type=c_type)
        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)

        if queryset.exists():
            type_label = "수입" if c_type == Category.CategoryType.INCOME else "지출"
            raise serializers.ValidationError(
                f"이미 {type_label} 카테고리에 '{name}'이(가) 존재합니다."
            )

        return data
