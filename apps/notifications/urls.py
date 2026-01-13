from django.urls import path

from .views import NotificationReadAPIView, UnreadNotificationListAPIView

urlpatterns = [
    path("unread/", UnreadNotificationListAPIView.as_view()),
    path("<int:pk>/read/", NotificationReadAPIView.as_view()),
]
