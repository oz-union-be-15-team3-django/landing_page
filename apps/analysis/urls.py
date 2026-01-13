from django.urls import path

from .views import (
    GenerateAnalysisView,
    SpendingAnalysisDetailView,
    SpendingAnalysisListView,
    SpendingComparisonView,
)

app_name = "analysis"

urlpatterns = [
    path("", SpendingAnalysisListView.as_view(), name="analysis-list"),
    path("<int:pk>/", SpendingAnalysisDetailView.as_view(), name="analysis-detail"),
    path("comparison/", SpendingComparisonView.as_view(), name="analysis-comparison"),
    path("generate/", GenerateAnalysisView.as_view(), name="analysis-generate"),
]
