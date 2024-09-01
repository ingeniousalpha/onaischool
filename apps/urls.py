from django.urls import include, path

urlpatterns = [
    # path("common/", include("apps.common.urls")),
    path("auth/", include("apps.authentication.urls")),
    path("content/", include("apps.content.urls")),
    path("cities/", include("apps.location.urls")),
    path("analytics/", include("apps.analytics.urls")),
    path("constructor/", include("apps.constructor.urls")),
]
