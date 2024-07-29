from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.generics import CreateAPIView, GenericAPIView
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.views import TokenRefreshView as DRFTokenRefreshView

from apps.common.mixins import PublicJSONRendererMixin, PrivateSONRendererMixin
# from apps.notifications.tasks import task_send_letter_for_email_confirmation
from .serializers import (
    SigninWithoutOTPSerializer, TokenRefreshSerializer, VerifyOTPSerializer,
    MyTokenObtainSerializer, SignupSerializer, AddChildrenSerializer)

User = get_user_model()


class SigninView(PublicJSONRendererMixin, TokenObtainPairView):
    """ Регистрация/Вход в систему по номеру телефона """

    queryset = User.objects.all()
    serializer_class = MyTokenObtainSerializer


class SignupView(PublicJSONRendererMixin, CreateAPIView):
    queryset = User.objects.all()
    serializer_class = SignupSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        # mobile_phone = serializer.validated_data["mobile_phone"]
        # send_otp(mobile_phone)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class AddChildView(PrivateSONRendererMixin, CreateAPIView):
    queryset = User.objects.all()
    serializer_class = AddChildrenSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        # mobile_phone = serializer.validated_data["mobile_phone"]
        # send_otp(mobile_phone)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class VerifyOTPV2View(PublicJSONRendererMixin, GenericAPIView):
    queryset = User.objects.all()
    serializer_class = VerifyOTPSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(data=serializer.validated_data)


class TokenRefreshView(PublicJSONRendererMixin, DRFTokenRefreshView):
    serializer_class = TokenRefreshSerializer


class MyFastTokenView(TokenObtainPairView):
    serializer_class = MyTokenObtainSerializer
