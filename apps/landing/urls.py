from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import *


urlpatterns = [
    path('', LandingView.as_view()),
    path('request', UserRequestView.as_view()),
]

