from django.urls import path

from .views import TransactionDetailView, TransactionListCreateView

app_name = "transactions"

urlpatterns = [
    path("", TransactionListCreateView.as_view(), name="transaction-list"),
    path("<int:pk>/", TransactionDetailView.as_view(), name="transaction-detail"),
]
