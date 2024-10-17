from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import *


urlpatterns = [
    path('/request', UserRequestView.as_view()),
    path('/question', UserQuestionView.as_view()),
]

