from django.db import models
from django.conf import settings


# 사용자id (FK)
# message (알림 메시지)
# is_read (읽음 여부)
# created_at (생성 시간)


class Notification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE) # 유저
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True) # 생성일시