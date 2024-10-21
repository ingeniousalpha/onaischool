from rest_framework import serializers

from apps.common.serializers import AbstractDescriptionSerializer, AbstractTitleSerializer
from apps.landing.models import *


class UserRequestSerializer(serializers.ModelSerializer):
    comment = serializers.CharField(required=False, allow_blank=True, write_only=True)
    text = serializers.CharField(required=False, allow_blank=True, write_only=True)

    class Meta:
        model = UserRequest
        fields = ["name", "phone", "comment", "text", "request_type"]


class AbstractImageSerializer(serializers.Serializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        abstract = True

    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image:
            return request.build_absolute_uri(obj.image.url)
        return ''


class BannerSerializer(AbstractTitleSerializer, AbstractImageSerializer, AbstractDescriptionSerializer):

    class Meta:
        model = Banner
        fields = ['id', 'title', 'description', 'image_url']


class ChampionSerializer(AbstractDescriptionSerializer, AbstractImageSerializer):

    class Meta:
        model = UserChampion
        fields = ['id', 'full_name', 'description', 'image_url']


class TeacherSerializer(AbstractDescriptionSerializer, AbstractImageSerializer):
    subject_name = serializers.SerializerMethodField()

    class Meta:
        model = Teacher
        fields = ['id', 'first_name', 'last_name', 'subject_name', 'image_url']

    def get_subject_name(self, obj):
        return obj.subject_name.translate()


class CourseFeatureSerializer(AbstractTitleSerializer):

    class Meta:
        model = CourseFeature
        fields = ['id', 'title']


class LandingCourseSerializer(AbstractTitleSerializer, AbstractDescriptionSerializer,):
    features = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = ['id', 'title', 'description', 'features']

    def get_features(self, obj):
        return CourseFeatureSerializer(obj.features, many=True, context=self.context).data


class ReviewSerializer(AbstractImageSerializer):

    class Meta:
        model = UserReview
        fields = ['id', 'image_url']


class LandingSerializer(serializers.Serializer):
    banners = serializers.SerializerMethodField()
    courses = serializers.SerializerMethodField()
    teachers = serializers.SerializerMethodField()
    champions = serializers.SerializerMethodField()
    reviews = serializers.SerializerMethodField()

    class Meta:
        fields = ['banners', 'courses', 'teachers', 'champions', 'reviews']

    def get_banners(self, obj):
        return BannerSerializer(Banner.objects.all(), many=True, context=self.context).data

    def get_courses(self, obj):
        return LandingCourseSerializer(Course.objects.all(), many=True, context=self.context).data

    def get_teachers(self, obj):
        return TeacherSerializer(Teacher.objects.all(), many=True, context=self.context).data

    def get_champions(self, obj):
        return ChampionSerializer(UserChampion.objects.all(), many=True, context=self.context).data

    def get_reviews(self, obj):
        return ReviewSerializer(UserReview.objects.all(), many=True, context=self.context).data
