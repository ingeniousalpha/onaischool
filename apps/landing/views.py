from django.shortcuts import render
from rest_framework.generics import CreateAPIView, ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.common.mixins import PrivateSONRendererMixin, PublicJSONRendererMixin
from apps.landing.models import UserRequest
from apps.landing.permissions import LandingTokenPermission
from apps.landing.serializers import UserRequestSerializer, LandingSerializer


class UserRequestView(PublicJSONRendererMixin, CreateAPIView):
    queryset = UserRequest.objects.all()
    serializer_class = UserRequestSerializer
    permission_classes = [LandingTokenPermission]


class LandingView(PublicJSONRendererMixin, APIView):
    queryset = None
    serializer_class = LandingSerializer
    permission_classes = [LandingTokenPermission]

    def get(self, request):
        return Response(data=LandingSerializer({}, context={"request": request}, many=False).data)