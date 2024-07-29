from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import (
    CatalogView,
    CourseView
)

urlpatterns = [

]

router = DefaultRouter()
router.register('directions', CatalogView, basename='content-directions')
router.register('course', CourseView, basename='content-directions')

urlpatterns += router.urls
