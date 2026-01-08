from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from .models import Account

User = get_user_model()


class AccountTestCase(TestCase):
    """계좌 API 테스트"""

    def setUp(self):
        """테스트 설정"""
        self.client = APIClient()
        self.user = User.objects.create_user(
            email="test@example.com", password="testpass123"
        )
        self.client.force_authenticate(user=self.user)

    def test_create_account(self):
        """계좌 생성 테스트"""
        data = {
            "account_number": "1234567890",
            "account_name": "테스트 계좌",
            "bank_name": "테스트 은행",
        }
        response = self.client.post("/api/accounts/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Account.objects.count(), 1)
        self.assertEqual(Account.objects.get().account_number, "1234567890")

    def test_list_accounts(self):
        """계좌 목록 조회 테스트"""
        Account.objects.create(
            user=self.user,
            account_number="1111111111",
            account_name="계좌1",
            bank_name="은행1",
        )
        Account.objects.create(
            user=self.user,
            account_number="2222222222",
            account_name="계좌2",
            bank_name="은행2",
        )

        response = self.client.get("/api/accounts/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 2)

    def test_retrieve_account(self):
        """계좌 상세 조회 테스트"""
        account = Account.objects.create(
            user=self.user,
            account_number="3333333333",
            account_name="계좌3",
            bank_name="은행3",
        )

        response = self.client.get(f"/api/accounts/{account.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["account_number"], "3333333333")

    def test_delete_account(self):
        """계좌 삭제 테스트"""
        account = Account.objects.create(
            user=self.user,
            account_number="4444444444",
            account_name="계좌4",
            bank_name="은행4",
        )

        response = self.client.delete(f"/api/accounts/{account.id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Account.objects.count(), 0)

    def test_account_update_forbidden(self):
        """계좌 수정 불가 테스트"""
        account = Account.objects.create(
            user=self.user,
            account_number="5555555555",
            account_name="계좌5",
            bank_name="은행5",
        )

        data = {"account_name": "수정된 계좌명"}
        response = self.client.patch(
            f"/api/accounts/{account.id}/", data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_only_sees_own_accounts(self):
        """사용자는 자신의 계좌만 조회 가능"""
        other_user = User.objects.create_user(
            email="other@example.com", password="testpass123"
        )

        Account.objects.create(
            user=self.user,
            account_number="6666666666",
            account_name="내 계좌",
            bank_name="은행6",
        )
        Account.objects.create(
            user=other_user,
            account_number="7777777777",
            account_name="다른 사용자 계좌",
            bank_name="은행7",
        )

        response = self.client.get("/api/accounts/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["account_number"], "6666666666")
