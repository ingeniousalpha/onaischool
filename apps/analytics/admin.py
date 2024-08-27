from django.contrib import admin
from localized_fields.admin import LocalizedFieldsAdminMixin

from apps.analytics.models import Question, Quiz, AnswerOption, EntranceExam, EntranceExamSubject, ExamQuestion, \
    ExamAnswerOption


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


class AssessmentInline(admin.StackedInline):
    model = EntranceExam
    fields = ('id', 'duration')
    extra = 0


class AssessmentSubjectInline(admin.StackedInline):
    model = EntranceExamSubject
    fields = ('id', 'title', 'max_score', 'questions_amount')
    extra = 0


class AssessmentQuestionInline(admin.StackedInline):
    model = ExamQuestion
    fields = ('id', 'title', 'image')
    extra = 0


class AssessmentAnswerOptionInline(admin.StackedInline):
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
    list_filter = ('quiz',)
    inlines = [AnswerOptionInline]


@admin.register(EntranceExam)
class AssessmentAdmin(LocalizedFieldsAdminMixin, admin.ModelAdmin):
    ...
    # inlines = [AssessmentSubjectInline]


@admin.register(EntranceExamSubject)
class AssessmentSubjectAdmin(LocalizedFieldsAdminMixin, admin.ModelAdmin):
    inlines = [AssessmentQuestionInline]


@admin.register(ExamQuestion)
class AssessmentQuestionAdmin(LocalizedFieldsAdminMixin, admin.ModelAdmin):
    inlines = [AssessmentAnswerOptionInline]


