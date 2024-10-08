from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.conf import settings

from apps.common.views import dashboard_view

urlpatterns = [
    path('admin/', admin.site.urls),
    # path('ckeditor/', include('ckeditor_uploader.urls')),
    path('dashboard/', dashboard_view),
    path("api/", include("apps.urls")),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.STATIC_URL,
        document_root=settings.STATIC_ROOT
    )
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )
