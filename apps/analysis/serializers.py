from rest_framework import serializers

from .models import SpendingAnalysis


class SpendingAnalysisSerializer(serializers.ModelSerializer):
    """소비 분석 데이터 Serializer"""

    analysis_type_display = serializers.CharField(
        source="get_analysis_type_display", read_only=True
    )

    class Meta:
        model = SpendingAnalysis
        fields = (
            "id",
            "analysis_type",
            "analysis_type_display",
            "start_date",
            "end_date",
            "total_income",
            "total_expense",
            "net_amount",
            "transaction_count",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "created_at",
            "updated_at",
        )


class SpendingComparisonSerializer(serializers.Serializer):
    """소비 비교 데이터 Serializer (시각화용)"""

    period = serializers.CharField()
    total_income = serializers.DecimalField(max_digits=15, decimal_places=2)
    total_expense = serializers.DecimalField(max_digits=15, decimal_places=2)
    net_amount = serializers.DecimalField(max_digits=15, decimal_places=2)
    transaction_count = serializers.IntegerField()
