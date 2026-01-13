from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

urlpatterns = [
    # Admin site
    path("admin/", admin.site.urls),
    # drf-spectacular
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path("swagger/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger"),  # noqa
    path("redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
    # apps
    path("users/", include("apps.users.urls")),
    path("accounts/", include("apps.accounts.urls")),
    path("transactions/", include("apps.transactions.urls")),
    path("categories/", include("apps.categories.urls")),
]

# Debug Toolbar 설정
if settings.DEBUG:
    try:
        import debug_toolbar

        urlpatterns = [
            path("__debug__/", include(debug_toolbar.urls)),
        ] + urlpatterns
    except ImportError:  # 라이브러리가 설치되지 않았을 경우
        pass
