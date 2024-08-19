from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline
from localized_fields.admin import LocalizedFieldsAdminMixin
from adminsortable2.admin import SortableAdminMixin, SortableInlineAdminMixin

from apps.analytics.admin import QuizInline, AssessmentInline
from apps.common.admin import ReadOnlyMixin
from apps.content.models import *


class SubjectInline(admin.StackedInline):
    model = Subject
    fields = ('id', 'name', 'direction')
    extra = 0


class CourseInline(admin.StackedInline):
    model = Course
    fields = ('id', 'name', 'subject', 'grade',)
    extra = 0


class TopicInline(admin.StackedInline):
    model = Topic
    fields = ('id', 'name', 'description', 'video_link', 'image', 'chapter')
    extra = 0


@admin.register(School)
class SchoolAdmin(LocalizedFieldsAdminMixin, admin.ModelAdmin):
    list_display = ('id', 'name', 'priority')


@admin.register(Direction)
class DirectionAdmin(LocalizedFieldsAdminMixin, admin.ModelAdmin):
    list_display = ('id', 'name', 'description', 'image', 'priority')
    inlines = [SubjectInline, AssessmentInline]


@admin.register(Subject)
class SubjectAdmin(LocalizedFieldsAdminMixin, admin.ModelAdmin):
    list_display = ('id', 'name', 'direction', 'priority')
    inlines = [CourseInline, QuizInline]


@admin.register(Course)
class CourseAdmin(LocalizedFieldsAdminMixin, admin.ModelAdmin):
    list_display = ('id', 'name', 'subject', 'grade', 'priority')
    inlines = [QuizInline]


@admin.register(Chapter)
class ChapterAdmin(LocalizedFieldsAdminMixin, admin.ModelAdmin):
    list_display = ('id', 'name', 'quarter', 'course', 'priority')
    inlines = [TopicInline]


@admin.register(Topic)
class TopicAdmin(LocalizedFieldsAdminMixin, admin.ModelAdmin):
    list_display = ('id', 'name', 'description', 'video_link', 'image', 'chapter', 'priority')
    inlines = [QuizInline]