from rest_framework.generics import ListAPIView
from rest_framework.viewsets import ReadOnlyModelViewSet

from apps.common.mixins import PrivateSONRendererMixin
from apps.content.models import Direction, Course
from apps.content.serializers import DirectionSerializer, DirectionRetriveSerializer, CourseSerializer


class CatalogView(PrivateSONRendererMixin, ReadOnlyModelViewSet):
    queryset = Direction.objects.all()
    serializer_class = DirectionSerializer

    def get_serializer_class(self):
        if self.action == "retrieve":
            return DirectionRetriveSerializer
        return DirectionSerializer


class CourseView(PrivateSONRendererMixin, ReadOnlyModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer

    def get_serializer_class(self):
        if self.action == "retrieve":
            return CourseSerializer
        return CourseSerializer
