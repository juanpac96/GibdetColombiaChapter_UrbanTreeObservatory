from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path("admin/", admin.site.urls),
    # API endpoints
    path(
        "api/v1/",
        include(
            [
                # Authentication
                path(
                    "auth/",
                    include(
                        [
                            path(
                                "token/",
                                TokenObtainPairView.as_view(),
                                name="token_obtain_pair",
                            ),
                            path(
                                "token/refresh/",
                                TokenRefreshView.as_view(),
                                name="token_refresh",
                            ),
                        ]
                    ),
                ),
                # App endpoints
                # path("accounts/", include("apps.accounts.urls")),
                path("trees/", include("apps.trees.urls")),
                # path("reports/", include("apps.reports.urls")),
                # path("analysis/", include("apps.analysis.urls")),
            ]
        ),
    ),
    # Development tools
    path("api-auth/", include("rest_framework.urls")),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

    # Debug toolbar
    import debug_toolbar

    urlpatterns += [
        path("__debug__/", include(debug_toolbar.urls)),
    ]
