from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

User = get_user_model()


class UserTestCase(TestCase):
    """사용자 API 테스트"""

    def setUp(self):
        """테스트 설정"""
        self.client = APIClient()

    def test_register_user(self):
        """회원가입 테스트"""
        data = {
            "email": "test@example.com",
            "password": "testpass123",
            "password2": "testpass123",
            "nickname": "테스트유저",
        }
        response = self.client.post("/api/users/signup/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.get().email, "test@example.com")

    def test_login_user(self):
        """로그인 테스트"""
        User.objects.create_user(email="test@example.com", password="testpass123")

        data = {"email": "test@example.com", "password": "testpass123"}
        response = self.client.post("/api/users/login/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access_token", response.cookies)
        self.assertIn("refresh_token", response.cookies)

    def test_profile_retrieve(self):
        """프로필 조회 테스트"""
        user = User.objects.create_user(
            email="test@example.com", password="testpass123", nickname="테스트유저"
        )
        self.client.force_authenticate(user=user)

        response = self.client.get("/api/users/profile/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], "test@example.com")
        self.assertEqual(response.data["nickname"], "테스트유저")

    def test_profile_update(self):
        """프로필 수정 테스트"""
        user = User.objects.create_user(
            email="test@example.com", password="testpass123", nickname="원본닉네임"
        )
        self.client.force_authenticate(user=user)

        data = {"nickname": "수정된닉네임"}
        response = self.client.patch("/api/users/profile/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        user.refresh_from_db()
        self.assertEqual(user.nickname, "수정된닉네임")

    def test_profile_delete(self):
        """프로필 삭제 테스트"""
        user = User.objects.create_user(
            email="test@example.com", password="testpass123"
        )
        self.client.force_authenticate(user=user)

        response = self.client.delete("/api/users/profile/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "Deleted successfully")
        self.assertEqual(User.objects.count(), 0)
