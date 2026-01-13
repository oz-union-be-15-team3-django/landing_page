"""
통합 테스트 파일
가계부 애플리케이션의 전체 워크플로우를 테스트합니다.
"""
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from apps.accounts.models import Account
from apps.categories.models import Category
from apps.transactions.models import Transaction

User = get_user_model()


class IntegrationTestCase(TestCase):
    """전체 애플리케이션 통합 테스트"""

    def setUp(self):
        """테스트 설정"""
        self.client = APIClient()

    def test_full_workflow(self):
        """전체 워크플로우 테스트: 회원가입 -> 계좌 생성 -> 카테고리 생성 -> 거래내역 생성"""
        # 1. 회원가입
        signup_data = {
            "username": "testuser",
            "email": "testuser@example.com",
            "password": "testpass123",
            "nickname": "테스트유저",
        }
        response = self.client.post("/users/signup/", signup_data, format="json")
        if response.status_code != status.HTTP_201_CREATED:
            print(f"회원가입 실패: {response.status_code}, {response.data}")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)

        user = User.objects.get(email="testuser@example.com")
        self.client.force_authenticate(user=user)

        # 2. 계좌 생성
        account_data = {
            "account_number": "1234567890",
            "account_name": "테스트 계좌",
            "bank_name": "테스트 은행",
        }
        response = self.client.post("/accounts/", account_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Account.objects.count(), 1)

        account = Account.objects.get()
        self.assertEqual(account.account_number, "1234567890")
        self.assertEqual(account.balance, Decimal("0.00"))

        # 3. 카테고리 생성 (수입)
        income_category_data = {
            "name": "급여_workflow",
            "category_type": "Deposit",
        }
        response = self.client.post(
            "/categories/", income_category_data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # 카테고리가 생성되었는지 확인 (이전 테스트 데이터와 격리)
        income_category = Category.objects.filter(
            user=user, name="급여_workflow", category_type="Deposit"
        ).first()
        self.assertIsNotNone(income_category)

        # 4. 카테고리 생성 (지출)
        expense_category_data = {
            "name": "식비_workflow",
            "category_type": "WITHDRAWAL",
        }
        response = self.client.post(
            "/categories/", expense_category_data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # 카테고리가 생성되었는지 확인
        expense_category = Category.objects.filter(
            user=user, name="식비_workflow", category_type="WITHDRAWAL"
        ).first()
        self.assertIsNotNone(expense_category)

        # 5. 입금 거래 생성
        deposit_data = {
            "account": account.id,
            "transaction_type": "Deposit",
            "amount": "100000.00",
            "description": "월급 입금",
            "category": income_category.id,
        }
        response = self.client.post("/transactions/", deposit_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Transaction.objects.count(), 1)

        # 계좌 잔액 확인
        account.refresh_from_db()
        self.assertEqual(account.balance, Decimal("100000.00"))

        # 6. 출금 거래 생성
        withdrawal_data = {
            "account": account.id,
            "transaction_type": "WITHDRAWAL",
            "amount": "50000.00",
            "description": "식비 지출",
            "category": expense_category.id,
        }
        response = self.client.post("/transactions/", withdrawal_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Transaction.objects.count(), 2)

        # 계좌 잔액 확인
        account.refresh_from_db()
        self.assertEqual(account.balance, Decimal("50000.00"))

        # 7. 거래내역 목록 조회
        response = self.client.get("/transactions/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 2)

        # 8. 거래내역 필터링 (입금만)
        response = self.client.get("/transactions/?transaction_type=Deposit")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # 필터링된 결과 중에서 입금 거래만 확인
        deposit_transactions = [
            t for t in response.data["results"]
            if t["transaction_type"] == "Deposit" and t["account"] == account.id
        ]
        self.assertGreaterEqual(len(deposit_transactions), 1)
        self.assertEqual(deposit_transactions[0]["transaction_type"], "Deposit")

        # 9. 프로필 조회
        response = self.client.get("/users/profile/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], "testuser@example.com")
        self.assertEqual(response.data["nickname"], "테스트유저")

    def test_multiple_accounts_workflow(self):
        """여러 계좌를 사용한 워크플로우 테스트"""
        # 사용자 생성 및 인증
        user = User.objects.create_user(
            username="multiuser", email="multiuser@example.com", password="testpass123"
        )
        self.client.force_authenticate(user=user)

        # 계좌 2개 생성
        account1 = Account.objects.create(
            user=user,
            account_number="1111111111",
            account_name="주 계좌",
            bank_name="은행1",
            balance=Decimal("100000.00"),
        )
        account2 = Account.objects.create(
            user=user,
            account_number="2222222222",
            account_name="저축 계좌",
            bank_name="은행2",
            balance=Decimal("50000.00"),
        )

        # 카테고리 생성
        category = Category.objects.create(
            user=user, name="이체", category_type="WITHDRAWAL"
        )

        # 계좌1에서 계좌2로 이체
        transfer_data = {
            "account": account1.id,
            "to_account": account2.id,
            "transaction_type": "TRANSFER",
            "amount": "30000.00",
            "description": "저축 이체",
            "category": category.id,
        }
        response = self.client.post("/transactions/", transfer_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # 계좌 잔액 확인
        account1.refresh_from_db()
        account2.refresh_from_db()
        self.assertEqual(account1.balance, Decimal("70000.00"))
        self.assertEqual(account2.balance, Decimal("80000.00"))

        # 각 계좌의 거래내역 확인
        response = self.client.get(f"/transactions/?account={account1.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)

        response = self.client.get(f"/transactions/?account={account2.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)

    def test_user_isolation(self):
        """사용자 간 데이터 격리 테스트"""
        # 사용자 1 생성
        user1 = User.objects.create_user(
            username="user1", email="user1@example.com", password="testpass123"
        )
        # 사용자 2 생성
        user2 = User.objects.create_user(
            username="user2", email="user2@example.com", password="testpass123"
        )

        # 사용자 1의 계좌 생성
        account1 = Account.objects.create(
            user=user1,
            account_number="1111111111",
            account_name="사용자1 계좌",
            bank_name="은행1",
        )

        # 사용자 2의 계좌 생성
        account2 = Account.objects.create(
            user=user2,
            account_number="2222222222",
            account_name="사용자2 계좌",
            bank_name="은행2",
        )

        # 사용자 1로 인증
        self.client.force_authenticate(user=user1)

        # 사용자 1은 자신의 계좌만 조회 가능
        response = self.client.get("/accounts/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        # 계좌번호는 마스킹되어 반환됨
        self.assertEqual(response.data["results"][0]["account_number"], "1111******")

        # 사용자 2의 계좌에 접근 시도 (404 또는 403)
        response = self.client.get(f"/accounts/{account2.id}/")
        self.assertIn(
            response.status_code,
            [status.HTTP_404_NOT_FOUND, status.HTTP_403_FORBIDDEN],
        )

    def test_category_transaction_integration(self):
        """카테고리와 거래내역 통합 테스트"""
        user = User.objects.create_user(
            username="categorytest", email="categorytest@example.com", password="testpass123"
        )
        self.client.force_authenticate(user=user)

        account = Account.objects.create(
            user=user,
            account_number="9999999999",
            account_name="테스트 계좌",
            bank_name="테스트 은행",
            balance=Decimal("0.00"),
        )

        # 수입 카테고리 생성
        income_category = Category.objects.create(
            user=user, name="급여_integration", category_type="Deposit"
        )

        # 지출 카테고리 생성
        expense_category = Category.objects.create(
            user=user, name="식비_integration", category_type="WITHDRAWAL"
        )

        # 카테고리별 거래내역 생성
        # 수입 거래
        deposit_data = {
            "account": account.id,
            "transaction_type": "Deposit",
            "amount": "200000.00",
            "description": "급여 입금",
            "category": income_category.id,
        }
        response = self.client.post("/transactions/", deposit_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # 지출 거래
        withdrawal_data = {
            "account": account.id,
            "transaction_type": "WITHDRAWAL",
            "amount": "50000.00",
            "description": "식비 지출",
            "category": expense_category.id,
        }
        response = self.client.post("/transactions/", withdrawal_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # 카테고리별 거래내역 확인
        response = self.client.get(f"/transactions/?category={income_category.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # 필터링된 결과 중에서 해당 카테고리인지 확인
        income_transactions = [t for t in response.data["results"] if t["category"] == income_category.id]
        self.assertGreaterEqual(len(income_transactions), 1)
        self.assertEqual(
            income_transactions[0]["category"], income_category.id
        )

        response = self.client.get(f"/transactions/?category={expense_category.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # 필터링된 결과 중에서 해당 카테고리인지 확인
        expense_transactions = [t for t in response.data["results"] if t["category"] == expense_category.id]
        self.assertGreaterEqual(len(expense_transactions), 1)
        self.assertEqual(
            expense_transactions[0]["category"], expense_category.id
        )

    def test_account_balance_calculation(self):
        """계좌 잔액 계산 정확성 테스트"""
        user = User.objects.create_user(
            username="balancetest", email="balancetest@example.com", password="testpass123"
        )
        self.client.force_authenticate(user=user)

        account = Account.objects.create(
            user=user,
            account_number="8888888888",
            account_name="잔액 테스트 계좌",
            bank_name="테스트 은행",
            balance=Decimal("100000.00"),
        )

        # 여러 거래 수행
        transactions = [
            {"type": "Deposit", "amount": "50000.00"},
            {"type": "WITHDRAWAL", "amount": "20000.00"},
            {"type": "Deposit", "amount": "30000.00"},
            {"type": "WITHDRAWAL", "amount": "10000.00"},
        ]

        expected_balance = Decimal("100000.00")
        for transaction in transactions:
            if transaction["type"] == "Deposit":
                expected_balance += Decimal(transaction["amount"])
            else:
                expected_balance -= Decimal(transaction["amount"])

            data = {
                "account": account.id,
                "transaction_type": transaction["type"],
                "amount": transaction["amount"],
                "description": f"{transaction['type']} 테스트",
            }
            response = self.client.post("/transactions/", data, format="json")
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # 최종 잔액 확인
        account.refresh_from_db()
        self.assertEqual(account.balance, expected_balance)
        self.assertEqual(account.balance, Decimal("150000.00"))

    def test_error_handling(self):
        """에러 처리 테스트"""
        user = User.objects.create_user(
            username="errortest", email="errortest@example.com", password="testpass123"
        )
        self.client.force_authenticate(user=user)

        account = Account.objects.create(
            user=user,
            account_number="7777777777",
            account_name="에러 테스트 계좌",
            bank_name="테스트 은행",
            balance=Decimal("10000.00"),
        )

        # 잔액 부족 시 출금 실패
        withdrawal_data = {
            "account": account.id,
            "transaction_type": "WITHDRAWAL",
            "amount": "50000.00",
            "description": "잔액 부족 테스트",
        }
        response = self.client.post("/transactions/", withdrawal_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # 계좌 잔액이 변경되지 않았는지 확인
        account.refresh_from_db()
        self.assertEqual(account.balance, Decimal("10000.00"))

        # 존재하지 않는 계좌로 거래 시도
        invalid_data = {
            "account": 99999,  # 존재하지 않는 ID
            "transaction_type": "Deposit",
            "amount": "1000.00",
        }
        response = self.client.post("/transactions/", invalid_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
