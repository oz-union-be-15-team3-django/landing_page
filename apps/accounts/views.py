from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from .models import Account
from .serializers import AccountDetailSerializer, AccountSerializer


@extend_schema_view(
    get=extend_schema(summary="내 계좌 목록 조회"),
    post=extend_schema(summary="새 계좌 등록"),
)
class AccountListCreateView(generics.ListCreateAPIView):
    """계좌 목록 조회 및 생성 API"""

    serializer_class = AccountSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Account.objects.filter(user=self.request.user, is_active=True).order_by(
            "-created_at"
        )

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


@extend_schema_view(
    get=extend_schema(summary="계좌 상세 조회"),
    patch=extend_schema(summary="계좌 정보 일부 수정"),
    put=extend_schema(summary="계좌 정보 전체 수정"),
    delete=extend_schema(summary="계좌 삭제"),
)
class AccountDetailView(generics.RetrieveUpdateDestroyAPIView):
    """계좌 상세 정보 조회, 수정, 삭제 API"""

    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Account.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        # 조회(GET) 요청일 때는 ReadOnly 시리얼라이저를 사용
        if self.request.method == "GET":
            return AccountDetailSerializer
        # 그 외 요청일 때는 수정이 가능한 시리얼라이저를 사용
        return AccountSerializer
