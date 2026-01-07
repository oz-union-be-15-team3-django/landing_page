from django.shortcuts import render, get_object_or_404
from .serializers import NotificationSerializer

from rest_framework.generics import ListAPIView
from .models import Notification
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response


class UnreadNotificationListAPIView(ListAPIView):
    serializer_class = NotificationSerializer

    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(
            user=self.request.user,
            is_read=False
        )

class NotificationReadAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def patch(self, request, pk):
        notification = get_object_or_404(Notification, pk=pk, user=request.user) 
        notification.is_read = True
        notification.save()
        return Response({"detail": "알림을 읽음 처리했습니다."})