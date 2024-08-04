from django.urls import path

from .views import (
    SigninView,
    SignupView,
    TokenRefreshView,
    VerifyOTPView,
    MyFastTokenView,
    AddChildView,
    AccountView,
    AuthByChildrenView
)

urlpatterns = [
    path("signin/", SigninView.as_view(), name="signin_view"),
    path("signup/", SignupView.as_view(), name="signup_view"),
    path("add-children/", AddChildView.as_view(), name="add-child-view"),
    path("accounts/", AccountView.as_view(), name="add-child-view"),
    path("by-children/", AuthByChildrenView.as_view(), name='signin-by-children'),
    # path("signin/fast_token", MyFastTokenView.as_view(), name="fast_token_view"),
    path("verify/", VerifyOTPView.as_view(), name="verify_otp_view"),
    path("refresh/", TokenRefreshView.as_view(), name="token_refresh_view"),
]


