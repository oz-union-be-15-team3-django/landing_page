from django.urls import path
from .views import UnreadNotificationListAPIView, NotificationReadAPIView

urlpatterns = [ 
    path("unread/", UnreadNotificationListAPIView.as_view()), 
    path("<int:pk>/read/", NotificationReadAPIView.as_view()),
]
