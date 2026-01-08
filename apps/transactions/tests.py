from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from apps.accounts.models import Account

from .models import Transaction

User = get_user_model()


class TransactionTestCase(TestCase):
    """거래내역 API 테스트"""

    def setUp(self):
        """테스트 설정"""
        self.client = APIClient()
        self.user = User.objects.create_user(
            email="test@example.com", password="testpass123"
        )
        self.account = Account.objects.create(
            user=self.user,
            account_number="1234567890",
            account_name="테스트 계좌",
            bank_name="테스트 은행",
            balance=Decimal("10000.00"),
        )
        self.client.force_authenticate(user=self.user)

    def test_create_deposit_transaction(self):
        """입금 거래 생성 테스트"""
        data = {
            "account": self.account.id,
            "transaction_type": "deposit",
            "amount": "5000.00",
            "description": "테스트 입금",
        }
        response = self.client.post("/api/transaction/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Transaction.objects.count(), 1)

        # 계좌 잔액 확인
        self.account.refresh_from_db()
        self.assertEqual(self.account.balance, Decimal("15000.00"))

    def test_create_withdrawal_transaction(self):
        """출금 거래 생성 테스트"""
        data = {
            "account": self.account.id,
            "transaction_type": "withdrawal",
            "amount": "3000.00",
            "description": "테스트 출금",
        }
        response = self.client.post("/api/transaction/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # 계좌 잔액 확인
        self.account.refresh_from_db()
        self.assertEqual(self.account.balance, Decimal("7000.00"))

    def test_create_withdrawal_insufficient_balance(self):
        """잔액 부족 시 출금 실패 테스트"""
        data = {
            "account": self.account.id,
            "transaction_type": "withdrawal",
            "amount": "20000.00",
            "description": "잔액 부족 출금",
        }
        response = self.client.post("/api/transaction/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_transactions(self):
        """거래내역 목록 조회 테스트"""
        Transaction.objects.create(
            account=self.account,
            user=self.user,
            transaction_type="deposit",
            amount=Decimal("1000.00"),
        )
        Transaction.objects.create(
            account=self.account,
            user=self.user,
            transaction_type="withdrawal",
            amount=Decimal("500.00"),
        )

        response = self.client.get("/api/transaction/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 2)

    def test_list_transactions_with_filter(self):
        """거래내역 필터링 테스트"""
        Transaction.objects.create(
            account=self.account,
            user=self.user,
            transaction_type="deposit",
            amount=Decimal("1000.00"),
        )
        Transaction.objects.create(
            account=self.account,
            user=self.user,
            transaction_type="withdrawal",
            amount=Decimal("500.00"),
        )

        # 입금만 필터링
        response = self.client.get("/api/transaction/?transaction_type=deposit")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["transaction_type"], "deposit")

        # 최소 금액 필터링
        response = self.client.get("/api/transaction/?min_amount=800")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)

    def test_retrieve_transaction(self):
        """거래내역 상세 조회 테스트"""
        transaction = Transaction.objects.create(
            account=self.account,
            user=self.user,
            transaction_type="deposit",
            amount=Decimal("2000.00"),
            description="테스트 거래",
        )

        response = self.client.get(f"/api/transaction/{transaction.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["amount"], "2000.00")
        self.assertEqual(response.data["description"], "테스트 거래")

    def test_update_transaction(self):
        """거래내역 수정 테스트"""
        transaction = Transaction.objects.create(
            account=self.account,
            user=self.user,
            transaction_type="deposit",
            amount=Decimal("1000.00"),
            description="원본 설명",
        )

        data = {"description": "수정된 설명", "amount": "1500.00"}
        response = self.client.patch(
            f"/api/transaction/{transaction.id}/", data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        transaction.refresh_from_db()
        self.assertEqual(transaction.description, "수정된 설명")

    def test_delete_transaction(self):
        """거래내역 삭제 테스트"""
        transaction = Transaction.objects.create(
            account=self.account,
            user=self.user,
            transaction_type="deposit",
            amount=Decimal("5000.00"),
        )
        initial_balance = self.account.balance

        response = self.client.delete(f"/api/transaction/{transaction.id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Transaction.objects.count(), 0)

        # 계좌 잔액이 복구되었는지 확인
        self.account.refresh_from_db()
        self.assertEqual(self.account.balance, initial_balance - Decimal("5000.00"))

    def test_user_only_sees_own_transactions(self):
        """사용자는 자신의 거래내역만 조회 가능"""
        other_user = User.objects.create_user(
            email="other@example.com", password="testpass123"
        )
        other_account = Account.objects.create(
            user=other_user,
            account_number="9999999999",
            account_name="다른 계좌",
            bank_name="은행9",
        )

        Transaction.objects.create(
            account=self.account,
            user=self.user,
            transaction_type="deposit",
            amount=Decimal("1000.00"),
        )
        Transaction.objects.create(
            account=other_account,
            user=other_user,
            transaction_type="deposit",
            amount=Decimal("2000.00"),
        )

        response = self.client.get("/api/transaction/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
