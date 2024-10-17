from django.contrib import admin
from localized_fields.admin import LocalizedFieldsAdminMixin

from apps.landing.models import UserRequest, UserQuestion, Teacher


@admin.register(UserRequest)
class UserRequestAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'phone']


@admin.register(UserQuestion)
class UserQuestionAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'phone']


@admin.register(Teacher)
class TeacherAdmin(LocalizedFieldsAdminMixin, admin.ModelAdmin):
    ...
