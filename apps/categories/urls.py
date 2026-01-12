from django.urls import path

from .views import CategoryListCreateView, CategoryRetrieveUpdateDestroyView

app_name = "categories"

urlpatterns = [
    # 카테고리 목록 조회 및 생성
    path("", CategoryListCreateView.as_view(), name="category-list-create"),
    # 카테고리 상세 조회, 수정, 삭제
    path(
        "<int:pk>/", CategoryRetrieveUpdateDestroyView.as_view(), name="category-detail"
    ),
]
