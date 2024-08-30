from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import (
    DirectionView,
    CourseView,
    TopicView,
    MyTopicView
)

urlpatterns = [
    path('topic/<int:pk>', TopicView.as_view()),
    path('my-topics', MyTopicView.as_view(), name='my-topics')
]

router = DefaultRouter()
router.register('directions', DirectionView, basename='content-directions')
router.register('course', CourseView, basename='content-directions')

urlpatterns += router.urls
