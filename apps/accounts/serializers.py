from rest_framework import serializers

from .models import Account


class AccountSerializer(serializers.ModelSerializer):
    """계좌 Serializer (목록 및 생성용)"""

    class Meta:
        model = Account
        fields = (
            "id",
            "user",
            "account_number",
            "account_name",
            "bank_name",
            "balance",
            "is_active",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "user",
            "balance",
            "is_active",
            "created_at",
            "updated_at",
        )

    def validate_account_number(self, value):
        """계좌번호 중복 검증"""
        if not self.instance and Account.objects.filter(account_number=value).exists():
            raise serializers.ValidationError("이미 존재하는 계좌번호입니다.")
        return value

    def to_representation(self, instance):
        """출력 시 계좌번호를 마스킹"""
        data = super().to_representation(instance)

        is_masking_on = self.context.get("masking", True)

        if is_masking_on:
            data["account_number"] = self._mask_account_number(instance.account_number)
        else:
            data["account_number"] = instance.account_number
        return data

    def _mask_account_number(self, account_number: str) -> str:
        if not account_number:
            return ""
        return account_number[:4] + "*" * max(
            len(account_number) - 4, 0
        )  # 앞 4자리 외 나머지를 * 처리


class AccountDetailSerializer(AccountSerializer):
    """계좌 상세 Serializer (조회용)"""

    class Meta(AccountSerializer.Meta):
        read_only_fields = AccountSerializer.Meta.read_only_fields + (
            "account_number",
            "account_name",
            "bank_name",
        )
