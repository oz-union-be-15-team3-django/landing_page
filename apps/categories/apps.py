from django.apps import AppConfig


class CategoriesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.categories"
    verbose_name = "Categories"

    def ready(self):
        # 서버 시작 시 시그널 파일을 임포트하여 등록합니다.
        import apps.categories.signals  # noqa
