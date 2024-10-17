from django.shortcuts import render
from rest_framework.generics import CreateAPIView

from apps.common.mixins import PrivateSONRendererMixin, PublicJSONRendererMixin
from apps.landing.models import UserRequest, UserQuestion
from apps.landing.serializers import UserRequestSerializer, UserQuestionSerializer


class UserRequestView(PublicJSONRendererMixin, CreateAPIView):
    queryset = UserRequest.objects.all()
    serializer_class = UserRequestSerializer


class UserQuestionView(PublicJSONRendererMixin, CreateAPIView):
    queryset = UserQuestion.objects.all()
    serializer_class = UserQuestionSerializer

