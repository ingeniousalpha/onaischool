import datetime

from django.contrib.auth import get_user_model, password_validation
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.serializers import TokenRefreshSerializer as BaseTokenRefreshSerializer
from six import text_type
from constance import config
from django.core.cache import cache

from apps.users.services import get_or_create_user_by_phone
from .exceptions import UserNotFound, UserAlreadyExists, SchoolNotFound, InCorrectPassword, AccessDenied, InvalidOTP
from .services import generate_access_and_refresh_tokens_for_user, validate_password
from .. import Roles
from ..content.models import School

User = get_user_model()


class SigninWithoutOTPSerializer(serializers.ModelSerializer):
    mobile_phone = serializers.CharField(write_only=True, required=False)
    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = (
            "mobile_phone",
            "password"
        )
        extra_kwargs = {
            "mobile_phone": {"write_only": True}
        }

    def validate(self, attrs):
        user = User.objects.filter(mobile_phone=attrs['mobile_phone']).first()
        if user is None:
            raise UserNotFound

        if not user.check_password(attrs['password']):
            raise InCorrectPassword

        return attrs

    def create(self, validated_data):
        user = User.objects.filter(mobile_phone=validated_data['mobile_phone'])

        return user

    def to_representation(self, instance):
        return generate_access_and_refresh_tokens_for_user(instance)


class PasswordResetRequestSerializer(serializers.Serializer):
    mobile_phone = serializers.CharField()

    def validate_mobile_phone(self, value):
        if not User.objects.filter(mobile_phone=value).exists():
            raise serializers.ValidationError("No user with this mobile_phone.")
        return value


class PasswordResetConfirmSerializer(serializers.Serializer):
    mobile_phone = serializers.CharField()
    otp_code = serializers.CharField()
    new_password = serializers.CharField(write_only=True)

    def validate(self, attrs):

        mobile_phone = attrs['mobile_phone']
        otp_code = attrs['otp_code']
        new_password = attrs['new_password']

        try:
            user = User.objects.get(mobile_phone=mobile_phone)
        except User.DoesNotExist:
            raise UserNotFound

        # cached_otp = cache.get(f'password_reset_otp_{user.id}')
        cached_otp = '1111'
        if cached_otp != otp_code:
            raise InvalidOTP

        attrs['user'] = user
        return attrs


class SignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password])
    re_password = serializers.CharField(write_only=True, required=True)
    mobile_phone = serializers.CharField(required=True, write_only=True)

    class Meta:
        model = User
        fields = ('mobile_phone', 'password', 're_password')

    def validate(self, attrs):
        if attrs['password'] != attrs['re_password']:
            raise serializers.ValidationError(
                {"password": "Password fields didn't match."})

        return attrs

    def to_representation(self, instance):
        return generate_access_and_refresh_tokens_for_user(instance)

    def create(self, validated_data):
        user = User.objects.filter(mobile_phone=validated_data['mobile_phone'])
        if user:
            raise UserAlreadyExists

        user = User.objects.create(mobile_phone=validated_data['mobile_phone'])
        user.set_password(validated_data['password'])
        user.save()

        return user


class AddChildrenSerializer(serializers.ModelSerializer):

    school_id = serializers.IntegerField()
    full_name = serializers.CharField()

    class Meta:
        model = User
        fields = (
            "full_name",
            "school_id",
            "grade"
        )

    def validate(self, attrs):
        user = self.context.get('request').user
        if user.role != Roles.PARENT:
            raise AccessDenied

        school = School.objects.filter(id=attrs['school_id']).first()
        if school is None:
            raise SchoolNotFound

        return attrs

    def create(self, validated_data):
        user = self.context.get('request').user
        if user is not None:
            child = User.objects.create(full_name=validated_data['full_name'], parent_id=user.id,
                                        grade=validated_data['grade'],
                                        school_id=validated_data['school_id'])

            return child
        return user


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
    mobile_phone = serializers.CharField(required=True, write_only=True)
    otp_code = serializers.CharField(required=True, write_only=True, min_length=4, max_length=4)

    def to_representation(self, instance):
        return generate_access_and_refresh_tokens_for_user(instance)

    def validate(self, attrs):
        if attrs['otp_code'] != '1111':
            raise InvalidOTP

        return attrs


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




class MyTokenObtainSerializer(serializers.Serializer):
    mobile_phone = serializers.CharField()
    password = serializers.CharField(write_only=True, required=False)

    def validate(self, attrs):
        user = User.objects.filter(mobile_phone=attrs['mobile_phone']).first()
        if not user:
            raise UserNotFound

        if not user.check_password(attrs['password']):
            raise InCorrectPassword

        refresh = TokenObtainPairSerializer.get_token(user)
        new_token = refresh.access_token

        if config.CUSTOM_TOKEN_TTL_TURNED_ON:
            new_token.set_exp(lifetime=datetime.timedelta(seconds=config.CUSTOM_TOKEN_TTL_SECONDS))
        return {
            "refresh_token": text_type(refresh),
            "access_token": text_type(new_token),
        }


class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'full_name']


class AuthByChildrenSerializer(serializers.Serializer):
    child_id = serializers.IntegerField(required=False)

    def validate(self, attrs):
        user = self.context.get('request').user
        child = User.objects.get(id=attrs['child_id'])
        if child is None:
            raise UserNotFound
        if not user.children.filter(id=child.id).exists():
            raise AccessDenied

        refresh = TokenObtainPairSerializer.get_token(child)
        new_token = refresh.access_token

        return {
            "refresh_token": text_type(refresh),
            "access_token": text_type(new_token),
        }


