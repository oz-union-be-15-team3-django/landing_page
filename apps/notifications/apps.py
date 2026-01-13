from django.apps import AppConfig


class NotificationConfig(AppConfig):
    name = "apps.notifications"

    def ready(self):
        try:
            import apps.notifications.signals  # 또는 notification.signals 썼다면 그걸로  # noqa: F401
        except ImportError:
            # analysis 앱이 아직 없을 때는 신호만 잠깐 꺼둠
            pass
