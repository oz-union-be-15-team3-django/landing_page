from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from apps.notification.models import Notification

User = get_user_model()


class TestNotificationAPI(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="test",
            email="test@example.com",  # 이메일 추가
            password="testpass123",
        )
        # self.client.login(username="test", password="testpass123")
        self.client.force_authenticate(user=self.user)

        # 안 읽은 알림
        self.unread_notif = Notification.objects.create(
            user=self.user,
            message="Unread",
            is_read=False,
        )

        # 이미 읽은 알림
        self.read_notif = Notification.objects.create(
            user=self.user,
            message="Read",
            is_read=True,
        )

    def test_unread_notifications_only_returns_unread(self):
        response = self.client.get("/notifications/unread/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], self.unread_notif.id)
