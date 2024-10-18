from django.contrib import admin
from localized_fields.admin import LocalizedFieldsAdminMixin

from apps.landing.models import *


@admin.register(Teacher)
class TeacherAdmin(LocalizedFieldsAdminMixin, admin.ModelAdmin):
    ...


@admin.register(Banner)
class BannerAdmin(LocalizedFieldsAdminMixin, admin.ModelAdmin):
    ...


@admin.register(UserReview)
class UserReviewAdmin(LocalizedFieldsAdminMixin, admin.ModelAdmin):
    ...


@admin.register(CourseFeature)
class CourseFeatureAdmin(LocalizedFieldsAdminMixin, admin.ModelAdmin):
    ...


@admin.register(Course)
class CourseAdmin(LocalizedFieldsAdminMixin, admin.ModelAdmin):
    filter_horizontal = ['features']


@admin.register(UserChampion)
class UserChampionAdmin(LocalizedFieldsAdminMixin, admin.ModelAdmin):
    ...


@admin.register(UserRequest)
class UserRequestAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'phone']
    list_filter = ['request_type']

