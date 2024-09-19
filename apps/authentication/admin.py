from django.contrib import admin
from rest_framework_simplejwt.token_blacklist.models import (
    BlacklistedToken,
    OutstandingToken,
)

from apps.authentication.models import SMSTemplate, SMSMessage, OTP

admin.site.unregister(BlacklistedToken)
admin.site.unregister(OutstandingToken)

admin.site.register(SMSTemplate)
admin.site.register(SMSMessage)
admin.site.register(OTP)
