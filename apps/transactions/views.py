# Create your views here.
from datetime import datetime

from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated

from .models import Transaction
from .serializers import TransactionDetailSerializer, TransactionSerializer


class TransactionListCreateView(ListCreateAPIView):
    """거래내역 목록 조회 및 생성 API - 필터링 지원"""

    permission_classes = [IsAuthenticated]
    serializer_class = TransactionSerializer

    def get_queryset(self):
        queryset = (
            Transaction.objects.filter(user=self.request.user, account__is_active=True)
            .select_related("account", "user")
            .order_by("-transaction_date")
        )

        transaction_type = self.request.query_params.get("transaction_type", None)
        min_amount = self.request.query_params.get("min_amount", None)
        max_amount = self.request.query_params.get("max_amount", None)
        start_date = self.request.query_params.get("start_date", None)
        end_date = self.request.query_params.get("end_date", None)

        if transaction_type:
            queryset = queryset.filter(transaction_type=transaction_type)

        if min_amount:
            queryset = queryset.filter(amount__gte=min_amount)

        if max_amount:
            queryset = queryset.filter(amount__lte=max_amount)

        if start_date:
            try:
                start_date = datetime.strptime(start_date, "%Y-%m-%d")
                queryset = queryset.filter(transaction_date__gte=start_date)
            except ValueError:
                pass

        if end_date:
            try:
                end_date = datetime.strptime(end_date, "%Y-%m-%d")
                queryset = queryset.filter(transaction_date__lte=end_date)
            except ValueError:
                pass

        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class TransactionDetailView(RetrieveUpdateDestroyAPIView):
    """거래내역 상세 조회/수정/삭제 API"""

    permission_classes = [IsAuthenticated]
    serializer_class = TransactionDetailSerializer

    def get_queryset(self):
        return Transaction.objects.filter(
            user=self.request.user, account__is_active=True
        ).select_related("account", "user")
