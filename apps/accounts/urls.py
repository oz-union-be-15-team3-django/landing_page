from django.urls import path

from .views import AccountDetailView, AccountListCreateView

app_name = "accounts"

urlpatterns = [
    path("", AccountListCreateView.as_view(), name="account-list"),
    path("<int:pk>/", AccountDetailView.as_view(), name="account-detail"),
]
