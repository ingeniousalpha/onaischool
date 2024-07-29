from rest_framework import serializers

from apps.common.serializers import AbstractNameSerializer, AbstractDescriptionSerializer, AbstractImageSerializer
from apps.content.models import Direction, Subject, Course, Chapter, Topic


class TopicSerializer(AbstractNameSerializer, AbstractImageSerializer):
    video_link = serializers.SerializerMethodField()
    class Meta:
        model = Topic
        fields = ['id', 'name', 'video_link', 'image']

    def get_video_link(self, obj):
        return obj.video_link.translate()


class TopicRetrieveSerializer(TopicSerializer, AbstractDescriptionSerializer):

    class Meta(TopicSerializer.Meta):
        fields = TopicSerializer.Meta.fields + ['description']


    def get_video_link(self, obj):
        return obj.video_link.translate()


class ChapterSerializer(AbstractNameSerializer):
    topics = serializers.SerializerMethodField()

    class Meta:
        model = Chapter
        fields = ['id', 'name', 'quarter', 'topics']

    def get_topics(self, obj):
        return TopicSerializer(obj.topics, many=True, context=self.context).data


class CourseSerializer(AbstractNameSerializer):
    chapters = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = ['id', 'name', 'grade', 'chapters']

    def get_chapters(self, obj):
        return ChapterSerializer(obj.chapters, many=True, context=self.context).data


class SubjectSerializer(AbstractNameSerializer):
    courses = serializers.SerializerMethodField()

    class Meta:
        model = Subject
        fields = ['id', 'name', 'courses']

    def get_courses(self, obj):
        return CourseSerializer(obj.courses, many=True, context=self.context).data


class DirectionSerializer(AbstractNameSerializer, AbstractDescriptionSerializer, AbstractImageSerializer):
    class Meta:
        model = Direction
        fields = [
            'id',
            'name',
            'description',
            'image'
        ]


class DirectionRetrieveSerializer(DirectionSerializer):
    subjects = serializers.SerializerMethodField()

    class Meta(DirectionSerializer.Meta):
        fields = DirectionSerializer.Meta.fields + ['subjects']

    def get_subjects(self, obj):
        return SubjectSerializer(obj.subjects, many=True, context=self.context).data
