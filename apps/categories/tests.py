from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from .models import Category

User = get_user_model()


class CategoryTestCase(TestCase):
    """카테고리 API 테스트"""

    def setUp(self):
        """테스트 설정"""
        self.client = APIClient()
        self.user = User.objects.create_user(
            email="test@example.com", password="testpass123"
        )
        self.client.force_authenticate(user=self.user)

    def test_create_income_category(self):
        """수입 카테고리 생성 테스트"""
        data = {"category_name": "급여", "category_type": "income"}
        response = self.client.post("/api/categories/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Category.objects.count(), 1)
        self.assertEqual(Category.objects.get().category_name, "급여")
        self.assertEqual(Category.objects.get().category_type, "income")

    def test_create_expense_category(self):
        """지출 카테고리 생성 테스트"""
        data = {"category_name": "식비", "category_type": "expense"}
        response = self.client.post("/api/categories/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Category.objects.get().category_type, "expense")

    def test_create_category_invalid_type(self):
        """잘못된 카테고리 유형 생성 실패 테스트"""
        data = {"category_name": "테스트", "category_type": "invalid_type"}
        response = self.client.post("/api/categories/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_categories(self):
        """카테고리 목록 조회 테스트"""
        Category.objects.create(
            user=self.user, category_name="급여", category_type="income"
        )
        Category.objects.create(
            user=self.user, category_name="식비", category_type="expense"
        )

        response = self.client.get("/api/categories/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_retrieve_category(self):
        """카테고리 상세 조회 테스트"""
        category = Category.objects.create(
            user=self.user, category_name="교통비", category_type="expense"
        )

        response = self.client.get(f"/api/categories/{category.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["category_name"], "교통비")
        self.assertEqual(response.data["category_type"], "expense")

    def test_update_category_patch(self):
        """카테고리 부분 수정 테스트 (PATCH)"""
        category = Category.objects.create(
            user=self.user, category_name="원본 카테고리", category_type="income"
        )

        data = {"category_name": "수정된 카테고리"}
        response = self.client.patch(
            f"/api/categories/{category.id}/", data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        category.refresh_from_db()
        self.assertEqual(category.category_name, "수정된 카테고리")
        self.assertEqual(category.category_type, "income")  # 수정하지 않은 필드는 유지

    def test_update_category_put(self):
        """카테고리 전체 수정 테스트 (PUT)"""
        category = Category.objects.create(
            user=self.user, category_name="원본 카테고리", category_type="income"
        )

        data = {"category_name": "수정된 카테고리", "category_type": "expense"}
        response = self.client.put(
            f"/api/categories/{category.id}/", data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        category.refresh_from_db()
        self.assertEqual(category.category_name, "수정된 카테고리")
        self.assertEqual(category.category_type, "expense")

    def test_delete_category(self):
        """카테고리 삭제 테스트"""
        category = Category.objects.create(
            user=self.user, category_name="삭제할 카테고리", category_type="expense"
        )

        response = self.client.delete(f"/api/categories/{category.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Category.objects.count(), 0)
        self.assertIn("message", response.data)
        self.assertEqual(response.data["message"], "Deleted successfully")

    def test_user_only_sees_own_categories(self):
        """사용자는 자신의 카테고리만 조회 가능"""
        other_user = User.objects.create_user(
            email="other@example.com", password="testpass123"
        )

        Category.objects.create(
            user=self.user, category_name="내 카테고리", category_type="income"
        )
        Category.objects.create(
            user=other_user,
            category_name="다른 사용자 카테고리",
            category_type="expense",
        )

        response = self.client.get("/api/categories/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["category_name"], "내 카테고리")

    def test_user_cannot_access_other_user_category(self):
        """다른 사용자의 카테고리에 접근 불가 테스트"""
        other_user = User.objects.create_user(
            email="other@example.com", password="testpass123"
        )

        other_category = Category.objects.create(
            user=other_user,
            category_name="다른 사용자 카테고리",
            category_type="income",
        )

        # 조회 시도
        response = self.client.get(f"/api/categories/{other_category.id}/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # 수정 시도
        data = {"category_name": "해킹 시도"}
        response = self.client.patch(
            f"/api/categories/{other_category.id}/", data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # 삭제 시도
        response = self.client.delete(f"/api/categories/{other_category.id}/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_category_requires_authentication(self):
        """인증 없이 카테고리 접근 불가 테스트"""
        self.client.force_authenticate(user=None)

        response = self.client.get("/api/categories/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.post("/api/categories/", {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
