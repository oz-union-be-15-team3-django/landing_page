from rest_framework import status
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Account
from .serializers import AccountDetailSerializer, AccountSerializer


class AccountListCreateView(ListCreateAPIView):
    """계좌 목록 조회 및 생성 API"""

    permission_classes = [IsAuthenticated]
    serializer_class = AccountSerializer

    def get_queryset(self):
        return Account.objects.filter(
            user=self.request.user, is_active=True
        ).select_related("user")

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class AccountDetailView(RetrieveUpdateDestroyAPIView):
    """계좌 상세 조회 및 삭제 API - 수정 불가"""

    permission_classes = [IsAuthenticated]
    serializer_class = AccountDetailSerializer

    def get_queryset(self):
        return Account.objects.filter(
            user=self.request.user, is_active=True
        ).select_related("user")

    def update(self, request, *args, **kwargs):
        return Response(
            {"error": "Account information cannot be modified after creation"},
            status=status.HTTP_403_FORBIDDEN,
        )

    def partial_update(self, request, *args, **kwargs):
        return Response(
            {"error": "Account information cannot be modified after creation"},
            status=status.HTTP_403_FORBIDDEN,
        )

    def perform_destroy(self, instance):
        instance.is_active = False
        instance.save(update_fields=["is_active"])
