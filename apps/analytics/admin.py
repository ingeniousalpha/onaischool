from django.contrib import admin
from localized_fields.admin import LocalizedFieldsAdminMixin

from apps.analytics.models import Question, Quiz, AnswerOption, EntranceExam, EntranceExamSubject, ExamQuestion, \
    ExamAnswerOption, EntranceExamPerDay


class QuizInline(admin.StackedInline):
    model = Quiz
    fields = ('id', 'type', 'questions_amount')
    extra = 0


class QuizQuestionInline(admin.StackedInline):
    model = Question
    fields = ('id', 'title', 'explain_video', 'type')
    extra = 0


class AnswerOptionInline(admin.StackedInline):
    model = AnswerOption
    fields = ('id', 'text', 'image', 'is_correct')
    extra = 0


class ExamInline(admin.StackedInline):
    model = EntranceExam
    fields = ('id', 'duration')
    extra = 0


class ExamSubjectInline(admin.StackedInline):
    model = EntranceExamSubject
    fields = ('id', 'title', 'max_score', 'questions_amount')
    extra = 0


class ExamPerDayInline(admin.StackedInline):
    model = EntranceExamPerDay
    fields = ('id', 'title', 'duration', 'passing_score')
    extra = 0


class ExamQuestionInline(admin.StackedInline):
    model = ExamQuestion
    fields = ('id', 'title', 'image', 'score')
    extra = 0


class ExamAnswerOptionInline(admin.StackedInline):
    model = ExamAnswerOption
    fields = ('id', 'text', 'image', 'is_correct')
    extra = 0


@admin.register(Quiz)
class QuizAdmin(LocalizedFieldsAdminMixin, admin.ModelAdmin):
    inlines = [QuizQuestionInline]


@admin.register(Question)
class QuestionAdmin(LocalizedFieldsAdminMixin, admin.ModelAdmin):
    fields = ('title', 'image', 'quiz', 'type', 'explain_video')
    list_display = ('id', 'title', 'quiz',)
    # list_filter = ('quiz',)
    inlines = [AnswerOptionInline]


@admin.register(EntranceExam)
class EntranceExamAdmin(LocalizedFieldsAdminMixin, admin.ModelAdmin):
    inlines = [ExamPerDayInline]


@admin.register(EntranceExamSubject)
class ExamSubjectAdmin(LocalizedFieldsAdminMixin, admin.ModelAdmin):
    inlines = [ExamQuestionInline]


@admin.register(ExamQuestion)
class ExamQuestionAdmin(LocalizedFieldsAdminMixin, admin.ModelAdmin):
    inlines = [ExamAnswerOptionInline]


