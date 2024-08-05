from itertools import groupby
from operator import itemgetter
from rest_framework import serializers

from apps.common.serializers import AbstractNameSerializer, AbstractDescriptionSerializer, AbstractImageSerializer
from apps.content.models import Direction, Subject, Course, Chapter, Topic, School


class SchoolSerializer(AbstractNameSerializer):
    class Meta:
        model = School
        fields = ['id', 'name']


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
        fields = ['id', 'name', 'topics']

    def get_topics(self, obj):
        return TopicSerializer(obj.topics, many=True, context=self.context).data


class CourseSerializer(AbstractNameSerializer):
    quarters = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = ['id', 'name', 'grade', 'quarters']

    def get_quarters(self, obj):
        chapters = obj.chapters.all().order_by('quarter', 'priority')
        grouped_chapters = groupby(chapters, key=lambda c: c.quarter)

        grouped_chapters_data = [
            {
                'quarter': key,
                'chapters': ChapterSerializer(list(groups), many=True, context=self.context).data
            }
            for key, groups in grouped_chapters
        ]

        return grouped_chapters_data


class CourseListSerializer(AbstractNameSerializer):
    class Meta:
        model = Course
        fields = ['id', 'name', 'grade']


class SubjectSerializer(AbstractNameSerializer):
    courses = serializers.SerializerMethodField()

    class Meta:
        model = Subject
        fields = ['id', 'name', 'courses']

    def get_courses(self, obj):
        return CourseSerializer(obj.courses, many=True, context=self.context).data


class SubjectListSerializer(SubjectSerializer):
    courses = serializers.SerializerMethodField()

    def get_courses(self, obj):
        return CourseListSerializer(obj.courses.order_by('grade'), many=True, context=self.context).data


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
        return SubjectListSerializer(obj.subjects, many=True, context=self.context).data
