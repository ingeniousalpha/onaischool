from django.contrib import admin
from localized_fields.admin import LocalizedFieldsAdminMixin
from adminsortable2.admin import SortableAdminMixin, SortableInlineAdminMixin

from apps.content.models import *


@admin.register(School)
class SchoolAdmin(LocalizedFieldsAdminMixin, admin.ModelAdmin):
    list_display = ('id', 'name', 'priority')


@admin.register(Direction)
class DirectionAdmin(LocalizedFieldsAdminMixin, admin.ModelAdmin):
    list_display = ('id', 'name', 'description', 'image', 'priority')


@admin.register(Subject)
class SubjectAdmin(LocalizedFieldsAdminMixin, admin.ModelAdmin):
    list_display = ('id', 'name', 'direction', 'priority')


@admin.register(Course)
class CourseAdmin(LocalizedFieldsAdminMixin, admin.ModelAdmin):
    list_display = ('id', 'name', 'subject', 'grade', 'priority')


@admin.register(Chapter)
class ChapterAdmin(LocalizedFieldsAdminMixin, admin.ModelAdmin):
    list_display = ('id', 'name', 'quarter', 'course', 'priority')


@admin.register(Topic)
class TopicAdmin(LocalizedFieldsAdminMixin, admin.ModelAdmin):
    list_display = ('id', 'name', 'description', 'video_link', 'image', 'chapter', 'priority')
