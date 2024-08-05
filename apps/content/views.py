from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.viewsets import ReadOnlyModelViewSet

from apps.common.mixins import PrivateSONRendererMixin
from apps.content.models import Direction, Course, Topic
from apps.content.serializers import DirectionSerializer, DirectionRetrieveSerializer, CourseSerializer, \
    TopicSerializer, TopicRetrieveSerializer


class DirectionView(PrivateSONRendererMixin, ReadOnlyModelViewSet):
    queryset = Direction.objects.all()
    serializer_class = DirectionSerializer

    def get_serializer_class(self):
        if self.action == "retrieve":
            return DirectionRetrieveSerializer
        return DirectionSerializer


class CourseView(PrivateSONRendererMixin, ReadOnlyModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer

    def get_serializer_class(self):
        if self.action == "retrieve":
            return CourseSerializer
        return CourseSerializer


class TopicView(PrivateSONRendererMixin, RetrieveAPIView):
    queryset = Topic.objects.all()
    serializer_class = TopicRetrieveSerializer
