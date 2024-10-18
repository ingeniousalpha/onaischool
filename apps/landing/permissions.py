from django.conf import settings

from apps.common.permissions import BaseTokenPermission


class LandingTokenPermission(BaseTokenPermission):
    token = settings.LANDING_SECRET_KEY
