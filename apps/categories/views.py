from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Category
from .serializers import (
    CategoryCreateRequestSerializer,
    CategoryResponseSerializer,
    CategoryUpdateRequestSerializer,
)


class CategoryListCreateView(generics.ListCreateAPIView):
    """
    카테고리 목록 조회 및 생성 API

    GET /api/categories/
    - 본인의 카테고리 목록을 조회합니다.

    POST /api/categories/
    - 새로운 카테고리를 생성합니다.
    """

    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """현재 로그인한 사용자의 카테고리만 반환"""
        return Category.objects.filter(user=self.request.user).select_related("user")

    def get_serializer_class(self):
        """요청 메서드에 따라 다른 serializer 사용"""
        if self.request.method == "POST":
            return CategoryCreateRequestSerializer
        return CategoryResponseSerializer

    def list(self, request, *args, **kwargs):
        """카테고리 목록 조회"""
        queryset = self.get_queryset()
        serializer = CategoryResponseSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        """카테고리 생성"""
        serializer = CategoryCreateRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # 카테고리 생성
        category = Category.objects.create(
            user=request.user,
            category_name=serializer.validated_data["category_name"],
            category_type=serializer.validated_data["category_type"],
        )

        response_serializer = CategoryResponseSerializer(category)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


class CategoryRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """
    카테고리 상세 조회, 수정, 삭제 API

    GET /api/categories/{id}/
    - 특정 카테고리의 상세 정보를 조회합니다.

    PATCH /api/categories/{id}/
    - 카테고리 정보를 부분 수정합니다.

    PUT /api/categories/{id}/
    - 카테고리 정보를 전체 수정합니다.

    DELETE /api/categories/{id}/
    - 카테고리를 삭제합니다.
    """

    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """현재 로그인한 사용자의 카테고리만 반환"""
        return Category.objects.filter(user=self.request.user).select_related("user")

    def get_serializer_class(self):
        """요청 메서드에 따라 다른 serializer 사용"""
        if self.request.method in ["PATCH", "PUT"]:
            return CategoryUpdateRequestSerializer
        return CategoryResponseSerializer

    def retrieve(self, request, *args, **kwargs):
        """카테고리 상세 조회"""
        instance = self.get_object()
        serializer = CategoryResponseSerializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        """카테고리 수정 (PUT)"""
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = CategoryUpdateRequestSerializer(
            instance, data=request.data, partial=partial
        )
        serializer.is_valid(raise_exception=True)

        # 카테고리 정보 업데이트
        if "category_name" in serializer.validated_data:
            instance.category_name = serializer.validated_data["category_name"]
        if "category_type" in serializer.validated_data:
            instance.category_type = serializer.validated_data["category_type"]
        instance.save()

        response_serializer = CategoryResponseSerializer(instance)
        return Response(response_serializer.data, status=status.HTTP_200_OK)

    def partial_update(self, request, *args, **kwargs):
        """카테고리 부분 수정 (PATCH)"""
        kwargs["partial"] = True
        return self.update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """카테고리 삭제"""
        instance = self.get_object()
        instance.delete()
        return Response({"message": "Deleted successfully"}, status=status.HTTP_200_OK)
