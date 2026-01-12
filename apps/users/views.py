from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from ..users.serializers import (
    LogoutSerializer,
    RegisterSerializer,
    UserSerializer,
)

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    """회원가입 API"""

    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    @extend_schema(
        summary="회원가입",
        description="새로운 사용자를 등록합니다. 이메일, 비밀번호, 닉네임, 휴대폰 번호가 필요합니다.",
        responses={
            201: UserSerializer,
            400: {"description": "입력 데이터 유효성 검사 실패"},
        },
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class LoginView(TokenObtainPairView):
    """로그인 API"""

    @extend_schema(
        summary="로그인(토큰 발급)",
        description="이메일과 비밀번호를 확인하여 Access 토큰과 Refresh 토큰을 발급합니다.",
        responses={
            200: {"description": "로그인 성공 및 토큰 발급"},
            401: {"description": "인증 실패 (이메일 혹은 비밀번호 오류)"},
        },
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class LogoutView(generics.GenericAPIView):
    """로그아웃 API"""

    permission_classes = [IsAuthenticated]
    serializer_class = LogoutSerializer

    @extend_schema(
        summary="로그아웃",
        description="전달받은 리프레시 토큰을 블랙리스트에 등록하여 무효화합니다.",
        responses={
            200: {"description": "로그아웃 성공"},
            400: {"description": "유효하지 않은 토큰 혹은 이미 로그아웃됨"},
        },
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            refresh_token = serializer.validated_data.get("refresh")
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(
                {"message": "Successfully logged out"}, status=status.HTTP_200_OK
            )
        except (TokenError, Exception) as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@extend_schema_view(
    get=extend_schema(
        summary="내 프로필 조회",
        description="현재 로그인한 사용자의 프로필 정보를 조회합니다.",
    ),
    patch=extend_schema(
        summary="내 프로필 수정",
        description="사용자의 닉네임이나 휴대폰 번호를 일부 수정합니다.",
    ),
    put=extend_schema(
        summary="내 프로필 수정(전체)",
        description="사용자의 프로필 정보를 전체 수정합니다.",
    ),
    delete=extend_schema(
        summary="회원 탈퇴",
        description="현재 로그인한 사용자의 계정을 삭제합니다. 이 작업은 되돌릴 수 없습니다.",
        responses={204: {"description": "탈퇴 성공"}},
    ),
)
class UserProfileView(generics.RetrieveUpdateDestroyAPIView):
    """내 프로필 RUD API"""

    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        # URL에서 pk를 받지 않고 현재 로그인한 유저 객체를 반환
        return self.request.user

    def perform_destroy(self, instance):
        # instance.delete() # hard delete
        # soft delete 처리
        instance.is_active = False
        instance.save()
