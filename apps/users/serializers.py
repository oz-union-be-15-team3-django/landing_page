from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from ..users.models import CustomUser


class RegisterSerializer(serializers.ModelSerializer):
    """회원가입 Serializer"""

    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password]
    )

    class Meta:
        model = CustomUser
        fields = ("username", "email", "password", "nickname", "phone_number")

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = CustomUser.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user


class LogoutSerializer(serializers.Serializer):
    """로그아웃(토큰 블랙리스트) 시리얼라이저"""

    refresh = serializers.CharField(help_text="무효화할 리프레시 토큰")


class UserSerializer(serializers.ModelSerializer):
    """기본 유저 정보 시리얼라이저"""

    class Meta:
        model = CustomUser
        fields = ("id", "email", "nickname", "phone_number", "date_joined", "is_active")
        read_only_fields = ("id", "date_joined", "is_active")
