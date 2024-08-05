from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.generics import CreateAPIView, GenericAPIView, ListAPIView, UpdateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.views import TokenRefreshView as DRFTokenRefreshView
from django.core.cache import cache
from apps.common.mixins import PublicJSONRendererMixin, PrivateSONRendererMixin
from .exceptions import UserNotFound
# from apps.notifications.tasks import task_send_letter_for_email_confirmation
from .serializers import (
    SigninWithoutOTPSerializer, TokenRefreshSerializer, VerifyOTPSerializer,
    MyTokenObtainSerializer, SignupSerializer, AddChildrenSerializer, AccountSerializer, AuthByChildrenSerializer,
    PasswordResetRequestSerializer, PasswordResetConfirmSerializer)

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


class PasswordResetRequestView(PublicJSONRendererMixin, APIView):

    def post(self, request, *args, **kwargs):
        serializer = PasswordResetRequestSerializer(data=request.data)
        if serializer.is_valid():
            mobile_phone = serializer.validated_data['mobile_phone']
            user = User.objects.get(mobile_phone=mobile_phone)
            return Response({}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetConfirmView(PublicJSONRendererMixin, APIView):
    def post(self, request, *args, **kwargs):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            new_password = serializer.validated_data['new_password']
            user.set_password(new_password)
            user.save()
            # cache.delete(f'password_reset_otp_{user.id}')

            return Response({}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AddChildView(PrivateSONRendererMixin, CreateAPIView):
    queryset = User.objects.all()
    serializer_class = AddChildrenSerializer

    def create(self, request, *args, **kwargs):
        print(request.data)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        # mobile_phone = serializer.validated_data["mobile_phone"]
        # send_otp(mobile_phone)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class VerifyOTPView(PublicJSONRendererMixin, GenericAPIView):
    queryset = User.objects.all()
    serializer_class = VerifyOTPSerializer

    def post(self, request):
        user = User.objects.filter(mobile_phone=request.data.get('mobile_phone')).first()
        if user is None:
            raise UserNotFound

        serializer = self.get_serializer(instance=user, data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(data=serializer.data)


class TokenRefreshView(PublicJSONRendererMixin, DRFTokenRefreshView):
    serializer_class = TokenRefreshSerializer


class MyFastTokenView(TokenObtainPairView):
    serializer_class = MyTokenObtainSerializer


class AccountView(PrivateSONRendererMixin, ListAPIView):
    queryset = User.objects.all()
    serializer_class = AccountSerializer

    def list(self, request, *args, **kwargs):
        data = self.get_serializer(request.user.children, many=True).data

        return Response(data, status=status.HTTP_200_OK)


class AuthByChildrenView(PrivateSONRendererMixin, APIView):
    serializer_class = AuthByChildrenSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid()
        return Response(serializer.validated_data, status=status.HTTP_200_OK)
