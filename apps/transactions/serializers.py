from rest_framework import serializers

from apps.accounts.serializers import AccountSerializer

from .models import Transaction


class TransactionSerializer(serializers.ModelSerializer):
    """거래내역 Serializer"""

    account_detail = AccountSerializer(source="account", read_only=True)
    transaction_type_display = serializers.CharField(
        source="get_transaction_type_display", read_only=True
    )

    class Meta:
        model = Transaction
        fields = (
            "id",
            "account",
            "account_detail",
            "user",
            "transaction_type",
            "transaction_type_display",
            "amount",
            "description",
            "transaction_date",
            "updated_at",
        )
        read_only_fields = ("id", "user", "transaction_date", "updated_at")

    def validate(self, attrs):
        account = attrs.get("account")
        transaction_type = attrs.get("transaction_type")
        amount = attrs.get("amount")
        request = self.context.get("request")

        if request and account and account.user_id != request.user.id:
            raise serializers.ValidationError(
                {"account": "본인 계좌로만 거래할 수 있습니다."}
            )

        if account and not account.is_active:
            raise serializers.ValidationError({"account": "비활성화된 계좌입니다."})

        if transaction_type == "withdrawal" and account.balance < amount:
            raise serializers.ValidationError({"amount": "계좌 잔액이 부족합니다."})

        return attrs


class TransactionDetailSerializer(serializers.ModelSerializer):
    """거래내역 상세 Serializer"""

    account_detail = AccountSerializer(source="account", read_only=True)
    transaction_type_display = serializers.CharField(
        source="get_transaction_type_display", read_only=True
    )
    user_email = serializers.EmailField(source="user.email", read_only=True)

    class Meta:
        model = Transaction
        fields = (
            "id",
            "account",
            "account_detail",
            "user",
            "user_email",
            "transaction_type",
            "transaction_type_display",
            "amount",
            "description",
            "transaction_date",
            "updated_at",
        )
        read_only_fields = ("id", "account", "user", "transaction_date", "updated_at")

    def validate(self, attrs):
        instance = self.instance
        if instance and not instance.account.is_active:
            raise serializers.ValidationError({"account": "비활성화된 계좌입니다."})
        if instance:
            transaction_type = attrs.get("transaction_type", instance.transaction_type)
            amount = attrs.get("amount", instance.amount)
            account = instance.account

            if transaction_type == "withdrawal":
                current_balance = account.balance
                if instance.transaction_type == "deposit":
                    current_balance -= instance.amount
                else:
                    current_balance += instance.amount

                if current_balance < amount:
                    raise serializers.ValidationError(
                        {"amount": "계좌 잔액이 부족합니다."}
                    )

        return attrs
