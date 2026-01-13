from analysis.models import Analysis
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Notification


@receiver(post_save, sender=Analysis)
def create_notification_when_analysis_created(sender, instance, created, **kwargs):
    if created:
        Notification.objects.create(
            user=instance.user,
            message="분석 결과가 생성되었습니다. 그래프를 확인해주세요.",
        )
