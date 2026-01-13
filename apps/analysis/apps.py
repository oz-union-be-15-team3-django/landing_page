from django.apps import AppConfig


class AnalysisConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.analysis"

    def ready(self):
        """앱이 준비되면 Celery tasks를 임포트"""
        import apps.analysis.tasks  # noqa
