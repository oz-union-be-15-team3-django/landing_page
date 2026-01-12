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
    delete=extend_schema(
        summary="거래 내역 삭제", description="거래 기록을 삭제합니다."
    ),
)
class TransactionDetailView(generics.RetrieveDestroyAPIView):
    """거래내역 상세 조회/수정/삭제 API"""

    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Transaction.objects.filter(
            user=self.request.user, account__is_active=True
        ).select_related("account", "user")
