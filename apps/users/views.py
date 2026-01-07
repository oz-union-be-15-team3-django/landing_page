from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.generics import CreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from ..users.serializers import (
    ProfileSerializer,
    ProfileUpdateResponseSerializer,
    ProfileUpdateSerializer,
    RegisterSerializer,
    UserSignupResponseSerializer,
)

User = get_user_model()


class RegisterView(CreateAPIView):
    """회원가입 API"""

    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = []

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        response_serializer = UserSignupResponseSerializer(user)
        headers = self.get_success_headers(response_serializer.data)
        return Response(
            response_serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )


class LoginView(TokenObtainPairView):
    """로그인 API"""

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        user = serializer.user
        token = serializer.validated_data.get("access")

        return Response(
            {
                "token": token,
                "user": {"id": user.id, "username": user.username, "email": user.email},
            },
            status=status.HTTP_200_OK,
        )


class LogoutView(CreateAPIView):
    """로그아웃 API"""

    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        try:
            refresh_token = request.data.get("refresh")

            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()

            return Response(
                {"message": "Successfully logged out"}, status=status.HTTP_200_OK
            )

        except TokenError:
            return Response(
                {"error": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class ProfileView(RetrieveUpdateDestroyAPIView):
    """회원정보 조회/수정/삭제 API"""

    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method in ["PATCH", "PUT"]:
            return ProfileUpdateSerializer
        return ProfileSerializer

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        response_serializer = ProfileUpdateResponseSerializer(instance)
        return Response(response_serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({"message": "Successfully deleted"}, status=status.HTTP_200_OK)
