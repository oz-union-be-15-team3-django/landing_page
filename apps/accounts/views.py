from drf_spectacular.utils import OpenApiParameter, extend_schema, extend_schema_view
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from .models import Account
from .serializers import AccountDetailSerializer, AccountSerializer


@extend_schema_view(
    get=extend_schema(
        summary="내 계좌 목록 조회",
        parameters=[
            OpenApiParameter(
                name="masking",
                type=bool,
                description="계좌번호 마스킹 여부 (true/false)",
                default=True,
            )
        ],
    ),
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

    def get_serializer_context(self):
        """URL 쿼리 파라미터에서 masking 값을 읽어 시리얼라이저에 전달"""
        context = super().get_serializer_context()
        masking_param = self.request.query_params.get("masking", "true").lower()

        # 문자열 'false'가 들어오면 False로 처리, 그 외에는 True
        context["masking"] = masking_param != "false"
        return context

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


@extend_schema_view(
    get=extend_schema(
        summary="계좌 상세 조회",
        parameters=[
            OpenApiParameter(
                name="masking",
                type=bool,
                description="계좌번호 마스킹 여부 (true/false)",
                default=True,
            )
        ],
    ),
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
        if self.request.method == "GET":
            return AccountDetailSerializer
        return AccountSerializer

    def get_serializer_context(self):
        """상세 뷰에서도 토글 기능이 작동하도록 컨텍스트 전달 로직 추가"""
        context = super().get_serializer_context()
        masking_param = self.request.query_params.get("masking", "true").lower()
        context["masking"] = masking_param != "false"
        return context
