from itertools import groupby
from operator import itemgetter

from django.db.models import Q
from rest_framework import serializers

from apps.common.mixins import UserPropertyMixin
from apps.common.serializers import AbstractNameSerializer, AbstractDescriptionSerializer, AbstractImageSerializer
from apps.content.exception import TopicNotFound
from apps.content.models import Direction, Subject, Course, Chapter, Topic, School
from apps.users.models import MyTopic


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


class DirectionWithNameSerializer(AbstractNameSerializer):

    class Meta:
        model = Direction
        fields = ['id', 'name']


class SubjectForMyCourseSerializer(AbstractNameSerializer):
    direction = DirectionWithNameSerializer()

    class Meta:
        model = Subject
        fields = ['id', 'name', 'direction']


class CourseWithNameSerializer(AbstractNameSerializer):
    subject = SubjectForMyCourseSerializer()

    class Meta:
        model = Course
        fields = ['id', 'name', 'grade', 'subject']


class TopicSerializerWithSubject(TopicSerializer, UserPropertyMixin):
    course_info = serializers.SerializerMethodField()
    quiz_completion = serializers.SerializerMethodField()

    class Meta(TopicSerializer.Meta):
        fields = TopicSerializer.Meta.fields + ['course_info', 'quiz_completion']

    def get_course_info(self, obj):
        if obj.chapter is not None:
            course = obj.chapter.course

            return CourseWithNameSerializer(course, context=self.context).data

    def get_quiz_completion(self, obj):
        quizzes = obj.quizzes.all()
        if quizzes:
            quiz = quizzes.first()
            questions_amount = quiz.questions_amount
            answered_count = self.user.user_quiz_questions.filter(Q(answers__isnull=False)
                                                                  & Q(quiz_id=quiz.id)).count()
        else:
            questions_amount = 0
            answered_count = 0

        return {
            'answered': answered_count,
            'questions_amount': questions_amount
        }


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


class MyTopicSerializer(serializers.ModelSerializer, UserPropertyMixin):
    topic = TopicSerializerWithSubject()

    class Meta:
        model = MyTopic
        fields = ['id', 'topic']


class MyTopicAddSerializer(serializers.ModelSerializer, UserPropertyMixin):
    class Meta:
        model = MyTopic
        fields = ['id', 'topic']

    def validate(self, attrs):
        topic_id = attrs['topic']
        return attrs

    def create(self, validated_data):
        topic = validated_data['topic']
        quizzes = topic.quizzes.all()
        completed = False
        if quizzes:
            quiz = quizzes.first()
            if quiz:
                questions_amount = quiz.questions_amount
                answered_count = self.user.user_quiz_questions.filter(
                    Q(answers__isnull=False) & Q(quiz_id=quiz.id)).count()
                completed = (questions_amount == answered_count)
        instance, created = MyTopic.objects.update_or_create(user=self.user, course_id=topic.chapter.course.id,
                                                             defaults={'is_completed': completed,
                                                                       'topic_id': topic.id})

        return instance
