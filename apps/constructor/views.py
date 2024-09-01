from django.shortcuts import render
from rest_framework.generics import ListAPIView
from rest_framework.response import Response

from apps.common.mixins import PrivateSONRendererMixin
from apps.constructor.serializers import MainPageSerializer


class MainPageView(PrivateSONRendererMixin, ListAPIView):
    serializer_class = MainPageSerializer
    pagination_class = None

    def list(self, request, *args, **kwargs):
        serializer = self.get_serializer(instance=request.user, context={'request': request})

        return Response(serializer.data)

