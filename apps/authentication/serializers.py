import datetime

from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.serializers import TokenRefreshSerializer as BaseTokenRefreshSerializer
from six import text_type

from apps.users.services import get_or_create_user_by_phone
from .exceptions import UserNotFound
from .services import generate_access_and_refresh_tokens_for_user

User = get_user_model()


class SigninWithoutOTPSerializer(serializers.ModelSerializer):
    club_branch = serializers.IntegerField(write_only=True)
    login = serializers.CharField(write_only=True, required=False)
    first_name = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = (
            "mobile_phone",
            "login",
            "club_branch",
            "first_name",
        )
        extra_kwargs = {
            "mobile_phone": {"write_only": True}
        }

    def to_representation(self, instance):
        return generate_access_and_refresh_tokens_for_user(instance)


class OLDSigninWithOTPSerializer(serializers.ModelSerializer):
    login = serializers.CharField(write_only=True, required=False)
    first_name = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = (
            "mobile_phone",
            "login",
            "first_name",
        )
        extra_kwargs = {
            "mobile_phone": {"write_only": True}
        }

    def create(self, validated_data):
        user, _ = get_or_create_user_by_phone(validated_data['mobile_phone'])
        club_user = validated_data.get('club_user')
        return user


class SigninWithOTPSerializer(serializers.Serializer):
    mobile_phone = serializers.CharField(write_only=True)
    club_branch = serializers.IntegerField(write_only=True)


class VerifyOTPSerializer(serializers.Serializer):
    club_branch = serializers.IntegerField(write_only=True)
    mobile_phone = serializers.CharField(required=True, write_only=True)
    otp_code = serializers.CharField(required=True, write_only=True, min_length=4, max_length=4)


class RegisterV2Serializer(serializers.ModelSerializer):
    club_branch = serializers.IntegerField(write_only=True)
    login = serializers.CharField(write_only=True, required=True)
    first_name = serializers.CharField(write_only=True, required=False)
    otp_code = serializers.CharField(required=True, write_only=True, min_length=4, max_length=4)

    class Meta:
        model = User
        fields = (
            "mobile_phone",
            "login",
            "club_branch",
            "first_name",
            "otp_code",
        )
        extra_kwargs = {
            "mobile_phone": {"write_only": True}
        }

    def to_representation(self, instance):
        return generate_access_and_refresh_tokens_for_user(instance)


class SigninByUsernameSerializer(serializers.Serializer):
    username = serializers.CharField()
    club_branch = serializers.IntegerField()


class TokenRefreshSerializer(BaseTokenRefreshSerializer):
    def validate(self, attrs):
        # JWTAuthentication.validate_refresh_token(attrs['refresh'])
        data = super().validate(attrs)
        return {
            "access_token": data['access'],
            "refresh_token": data['refresh'],
        }


CUSTOM_LIFETIME = datetime.timedelta(seconds=30)


class MyTokenObtainSerializer(serializers.Serializer):
    mobile_phone = serializers.CharField()

    def validate(self, attrs):
        user = User.objects.filter(mobile_phone=attrs['mobile_phone']).first()
        if not user:
            raise UserNotFound

        refresh = TokenObtainPairSerializer.get_token(user)
        new_token = refresh.access_token
        new_token.set_exp(lifetime=CUSTOM_LIFETIME)
        return {
            "refresh_token": text_type(refresh),
            "access_token": text_type(new_token),
        }
