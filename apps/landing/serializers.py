from rest_framework import serializers

from apps.landing.models import UserRequest, UserQuestion


class UserRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserRequest
        fields = "__all__"


class UserQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserQuestion
        fields = "__all__"
