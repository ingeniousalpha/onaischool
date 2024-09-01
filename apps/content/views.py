from rest_framework.generics import ListAPIView, RetrieveAPIView, ListCreateAPIView
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet

from apps.common.mixins import PrivateSONRendererMixin
from apps.content.models import Direction, Course, Topic
from apps.content.serializers import DirectionSerializer, DirectionRetrieveSerializer, CourseSerializer, \
    TopicSerializer, TopicRetrieveSerializer, MyTopicSerializer, MyTopicAddSerializer
from apps.users.models import MyTopic


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

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        user = request.user
        if user.current_topic is None:
            user.current_topic = instance
            user.save(update_fields=['current_topic'])
        else:
            if user.current_topic.priority < instance.priority:
                user.current_topic = instance
                user.save(update_fields=['current_topic'])
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class MyTopicView(PrivateSONRendererMixin, ListCreateAPIView):
    queryset = MyTopic.objects.all()
    serializer_class = MyTopicSerializer

    def create(self, request, *args, **kwargs):
        serializer_input = {'data': request.data, 'context': {'request': request}}
        serializer = MyTopicAddSerializer(**serializer_input)

        if serializer.is_valid(raise_exception=True):
            serializer.save()
        return Response({})

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        active = request.query_params.get('active', 'false').lower() == 'true'
        if active:
            queryset = self.get_queryset().filter(is_completed=False)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
