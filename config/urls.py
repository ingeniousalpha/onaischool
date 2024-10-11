from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.conf import settings

from apps.common.views import dashboard_view, get_schools, get_students, get_tasks_data

urlpatterns = [
    path('admin/', admin.site.urls),
    # path('ckeditor/', include('ckeditor_uploader.urls')),
    path('dashboard/', dashboard_view),
    path('get-schools/', get_schools, name='get_schools'),
    path('get-students/', get_students, name='get_students'),
    path('get-tasks-data/', get_tasks_data, name='get_tasks_data'),
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
