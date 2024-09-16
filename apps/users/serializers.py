from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from rest_framework import serializers

from apps.authentication.exceptions import SchoolNotFound
from apps.content.models import School
from apps.content.serializers import SchoolSerializer
from apps.location.serializers import CitySerializer
from apps.users.exceptions import PasswordsAreNotEqual, AvatarNotFound, NewPasswordInvalid
from apps.users.models import Avatar

User = get_user_model()


class UserSchoolSerializer(SchoolSerializer):
    city = CitySerializer()

    class Meta(SchoolSerializer.Meta):
        fields = SchoolSerializer.Meta.fields + ['city']


class AvatarSerializer(serializers.ModelSerializer):
    class Meta:
        model = Avatar
        fields = ['id', 'image']


class UserProfileSerializer(serializers.ModelSerializer):
    school = UserSchoolSerializer()
    avatar = AvatarSerializer()

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "full_name",
            "mobile_phone",
            "avatar",
            "grade",
            "school"
        ]


class UserUpdateSerializer(serializers.ModelSerializer):
    school_id = serializers.IntegerField()
    avatar_id = serializers.IntegerField()
    current_password = serializers.CharField(write_only=True, required=False)
    new_password = serializers.CharField(write_only=True, required=False)
    re_password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = [
            "full_name",
            "grade",
            "school_id",
            "avatar_id",
            "current_password",
            "new_password",
            "re_password"
        ]

    def validate(self, data):
        new_password = data.get('new_password')
        re_password = data.get('re_password')

        if new_password and re_password and new_password != re_password:
            raise PasswordsAreNotEqual

        if not School.objects.filter(id=data.get('school_id')).exists():
            raise SchoolNotFound

        if not Avatar.objects.filter(id=data.get('avatar_id')).exists():
            raise AvatarNotFound

        return data

    def update(self, instance, validated_data):
        current_password = validated_data.pop('current_password', None)
        new_password = validated_data.pop('new_password', None)

        instance.full_name = validated_data.get('full_name', instance.full_name)
        instance.grade = validated_data.get('grade', instance.grade)
        instance.school_id = validated_data.get('school_id', instance.school_id)
        instance.avatar_id = validated_data.get('avatar_id', instance.avatar_id)

        if current_password and new_password:
            if not instance.check_password(current_password):
                raise NewPasswordInvalid

            instance.password = make_password(new_password)

        instance.save()
        return instance
