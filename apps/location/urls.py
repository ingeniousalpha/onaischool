from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import (
    CitiesView,
)

urlpatterns = []

router = DefaultRouter()
router.register('', CitiesView, basename='cities-view')


urlpatterns += router.urls
