from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import MainPageView


urlpatterns = [
    path('main-page/', MainPageView.as_view()),
]
