from django.db import transaction
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from .models import Transaction
from .serializers import TransactionSerializer


@extend_schema_view(
    get=extend_schema(
        summary="내 거래 내역 목록",
        description="로그인한 사용자의 전체 거래 내역을 조회합니다.",
    ),
    post=extend_schema(
        summary="새 거래 등록",
        description="입금 또는 출금 거래를 생성하고 계좌 잔액을 업데이트합니다.",
    ),
)
class TransactionListCreateView(generics.ListCreateAPIView):
    """거래내역 목록 조회 및 생성 API"""

    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user).select_related(
            "account"
        )

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


@extend_schema_view(
    get=extend_schema(summary="거래 내역 상세"),
    put=extend_schema(summary="거래 내역 전체 수정"),
    patch=extend_schema(summary="거래 내역 일부 수정"),
    delete=extend_schema(summary="거래 내역 삭제"),
)
class TransactionDetailView(generics.RetrieveUpdateDestroyAPIView):
    """거래내역 상세 조회/수정/삭제 API"""

    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Transaction.objects.filter(
            user=self.request.user, account__is_active=True
        ).select_related("account", "user")

    @transaction.atomic
    def perform_destroy(self, instance):
        """삭제 전 잔액 복구 로직"""
        serializer = self.get_serializer(instance)
        # 'delete' 모드로 호출하여 삭제될 금액만큼 계좌 잔액을 반대로 조정합니다.
        serializer._update_account_balance(instance, mode="delete")
        # 이후 실제 거래 데이터 삭제
        instance.delete()
