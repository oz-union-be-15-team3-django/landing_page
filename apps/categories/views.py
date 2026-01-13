from drf_spectacular.utils import OpenApiParameter, extend_schema, extend_schema_view
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from .models import Category
from .serializers import CategorySerializer


@extend_schema_view(
    get=extend_schema(
        summary="카테고리 목록 조회",
        description="카테고리 목록을 조회합니다.",
        parameters=[
            OpenApiParameter(
                name="type", description="INCOME 또는 EXPENSE로 필터링", type=str
            )
        ],
    ),
    post=extend_schema(summary="커스텀 카테고리 생성"),
)
class CategoryListCreateView(generics.ListCreateAPIView):
    """카테고리 목록 조회 및 생성 뷰"""

    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # 로그인 사용자의 카테고리 반환
        queryset = Category.objects.filter(user=self.request.user)

        category_type = self.request.query_params.get("type", "")
        if category_type == "INCOME":
            queryset = queryset.filter(category_type=Category.CategoryType.INCOME)
        elif category_type == "EXPENSE":
            queryset = queryset.filter(category_type=Category.CategoryType.EXPENSE)

        return queryset.order_by("category_type", "name")

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


@extend_schema_view(
    get=extend_schema(summary="카테고리 상세 조회"),
    put=extend_schema(summary="카테고리 전체 수정"),
    patch=extend_schema(summary="카테고리 일부 수정"),
    delete=extend_schema(summary="카테고리 삭제"),
)
class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    """카테고리 상세 조회, 수정 및 삭제"""

    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Category.objects.filter(user=self.request.user)
