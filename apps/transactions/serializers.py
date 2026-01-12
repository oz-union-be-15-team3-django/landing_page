from django.db import transaction
from rest_framework import serializers

from .models import Transaction


class TransactionSerializer(serializers.ModelSerializer):
    """거래내역 Serializer"""

    account_name = serializers.CharField(source="account.account_name", read_only=True)
    to_account_name = serializers.CharField(
        source="to_account.account_name", read_only=True
    )
    bank_name = serializers.CharField(source="account.bank_name", read_only=True)

    class Meta:
        model = Transaction
        fields = (
            "id",
            "user",
            "account",
            "account_name",
            "to_account",
            "to_account_name",
            "bank_name",
            "transaction_type",
            "amount",
            "currency",
            "balance_after_transaction",
            "category",
            "description",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "user", "balance_after_transaction", "created_at")

    def validate(self, data):
        """계좌 소유권 및 잔액 검증"""
        user = self.context["request"].user
        account = data.get("account", getattr(self.instance, "account", None))
        t_type = data.get(
            "transaction_type", getattr(self.instance, "transaction_type", None)
        )
        amount = data.get("amount", getattr(self.instance, "amount", 0))

        if not account:
            raise serializers.ValidationError("계좌 정보가 필요합니다.")

        # 계좌 소유권 확인
        if account.user != user:
            raise serializers.ValidationError(
                "본인 소유의 계좌에서만 거래가 가능합니다."
            )

        # 출금 시 잔액 부족 확인
        if t_type in [
            Transaction.TransactionType.WITHDRAWAL,
            Transaction.TransactionType.TRANSFER,
        ]:
            current_balance = account.balance
            if self.instance and self.instance.account == account:
                current_balance += (
                    self.instance.amount
                    if self.instance.transaction_type
                    != Transaction.TransactionType.DEPOSIT
                    else -self.instance.amount
                )

            if current_balance < amount:
                raise serializers.ValidationError("계좌 잔액이 부족합니다.")

        # 이체 시 검증
        if t_type == Transaction.TransactionType.TRANSFER:
            to_account = data.get(
                "to_account", getattr(self.instance, "to_account", None)
            )
            if not to_account:
                raise serializers.ValidationError(
                    {"to_account": "이체 시 입금 계좌 선택은 필수입니다."}
                )
            if to_account == account:
                raise serializers.ValidationError(
                    {"to_account": "동일한 계좌로 이체할 수 없습니다."}
                )
            if to_account.user != user:
                raise serializers.ValidationError(
                    {"to_account": "본인 소유의 계좌로만 이체할 수 있습니다."}
                )

        return data

    @transaction.atomic
    def create(self, validated_data):
        """거래 생성 시 잔액 반영"""
        instance = Transaction(**validated_data)
        self._update_account_balance(instance, mode="create")
        instance.balance_after_transaction = instance.account.balance
        instance.save()
        return instance

    @transaction.atomic
    def update(self, instance, validated_data):
        """거래 수정 시 잔액 재계산 로직"""
        # 1. 기존 거래 효과 되돌리기 (Revert)
        self._update_account_balance(instance, mode="delete")

        # 2. 데이터 업데이트
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        # 3. 새로운 거래 효과 적용 (Apply)
        self._update_account_balance(instance, mode="create")

        # 4. 거래 후 잔액 기록 및 저장
        instance.balance_after_transaction = instance.account.balance
        instance.save()
        return instance

    def _update_account_balance(self, transaction_obj, mode="create"):
        """
        계좌 잔액 계산 로직
        mode: 'create' (반영), 'delete' (되돌리기)
        """
        account = transaction_obj.account
        if not account:
            return

        to_account = transaction_obj.to_account
        amount = transaction_obj.amount
        t_type = transaction_obj.transaction_type

        # 반영할 때는 multiplier가 1, 되돌릴 때는 -1
        multiplier = 1 if mode == "create" else -1

        if t_type == Transaction.TransactionType.DEPOSIT:
            account.balance += amount * multiplier
        elif t_type == Transaction.TransactionType.WITHDRAWAL:
            account.balance -= amount * multiplier
        elif t_type == Transaction.TransactionType.TRANSFER:
            account.balance -= amount * multiplier
            if to_account:
                to_account.balance += amount * multiplier
                to_account.save()

        account.save()
