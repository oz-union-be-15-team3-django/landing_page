from django.apps import AppConfig


class NotificationConfig(AppConfig):
    name = 'apps.notification'

    # def ready(self):
    #     import notification.signals
    def ready(self):
        try:
            import apps.notification.signals  # 또는 notification.signals 썼다면 그걸로
        except ImportError:
            # analysis 앱이 아직 없을 때는 신호만 잠깐 꺼둠
            pass