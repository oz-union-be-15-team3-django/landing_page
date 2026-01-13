from rest_framework import status
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import SpendingAnalysis
from .serializers import SpendingAnalysisSerializer, SpendingComparisonSerializer
from .tasks import generate_user_analysis


class SpendingAnalysisListView(ListAPIView):
    """소비 분석 데이터 목록 조회 API"""

    permission_classes = [IsAuthenticated]
    serializer_class = SpendingAnalysisSerializer

    def get_queryset(self):
        queryset = SpendingAnalysis.objects.filter(user=self.request.user)

        # 분석 타입 필터링
        analysis_type = self.request.query_params.get("analysis_type", None)
        if analysis_type:
            queryset = queryset.filter(analysis_type=analysis_type)

        return queryset.order_by("-start_date")


class SpendingAnalysisDetailView(RetrieveAPIView):
    """소비 분석 데이터 상세 조회 API"""

    permission_classes = [IsAuthenticated]
    serializer_class = SpendingAnalysisSerializer

    def get_queryset(self):
        return SpendingAnalysis.objects.filter(user=self.request.user)


class SpendingComparisonView(ListAPIView):
    """소비 비교 데이터 조회 API (시각화용)"""

    permission_classes = [IsAuthenticated]
    serializer_class = SpendingComparisonSerializer

    def get(self, request, *args, **kwargs):
        """주간/월간 소비 비교 데이터 반환"""
        user = request.user

        # 최근 4주간 주간 분석 데이터
        weekly_analyses = SpendingAnalysis.objects.filter(
            user=user, analysis_type="weekly"
        ).order_by("-start_date")[:4]

        # 최근 3개월간 월간 분석 데이터
        monthly_analyses = SpendingAnalysis.objects.filter(
            user=user, analysis_type="monthly"
        ).order_by("-start_date")[:3]

        weekly_data = []
        for analysis in weekly_analyses:
            weekly_data.append(
                {
                    "period": f"{analysis.start_date.strftime('%Y-%m-%d')} ~ {analysis.end_date.strftime('%Y-%m-%d')}",
                    "total_income": analysis.total_income,
                    "total_expense": analysis.total_expense,
                    "net_amount": analysis.net_amount,
                    "transaction_count": analysis.transaction_count,
                }
            )

        monthly_data = []
        for analysis in monthly_analyses:
            monthly_data.append(
                {
                    "period": f"{analysis.start_date.strftime('%Y-%m')}",
                    "total_income": analysis.total_income,
                    "total_expense": analysis.total_expense,
                    "net_amount": analysis.net_amount,
                    "transaction_count": analysis.transaction_count,
                }
            )

        return Response(
            {
                "weekly": weekly_data,
                "monthly": monthly_data,
            },
            status=status.HTTP_200_OK,
        )


class GenerateAnalysisView(RetrieveAPIView):
    """분석 데이터 수동 생성 API"""

    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        """현재 사용자의 분석 데이터 생성"""
        user = request.user

        # Celery 태스크 비동기 실행
        task = generate_user_analysis.delay(user.id)

        return Response(
            {
                "message": "Analysis generation started",
                "task_id": task.id,
            },
            status=status.HTTP_202_ACCEPTED,
        )
