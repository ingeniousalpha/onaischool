from django.contrib import admin
from django.core.exceptions import ValidationError
from django import forms
import pandas as pd
import re
from localized_fields.admin import LocalizedFieldsAdminMixin

from apps.analytics.models import Question, Quiz, AnswerOption, EntranceExam, EntranceExamSubject, ExamQuestion, \
    ExamAnswerOption, EntranceExamPerDay, DiagnosticExam, DiagnosticExamQuestion, DiagnosticExamAnswerOption, \
    QuestionType
from apps.analytics.utils import regex_options, remove_latex_bracket
from apps.content.models import Topic


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
    search_fields = ['topic__name__ru', 'topic__name__kk']
    list_filter = ('subject', 'course', 'topic')


@admin.register(Question)
class QuestionAdmin(LocalizedFieldsAdminMixin, admin.ModelAdmin):
    fields = (
        'title',
        'image',
        'quiz',
        'type',
        'explain_video',
        'explanation_answer',
    )
    search_fields = ('title__ru', 'title__kk')
    list_display = ('id', 'title', 'quiz',)
    list_filter = ('quiz',)
    inlines = [AnswerOptionInline]


@admin.register(EntranceExam)
class EntranceExamAdmin(LocalizedFieldsAdminMixin, admin.ModelAdmin):
    inlines = [ExamPerDayInline]
    search_fields = ('title__ru', 'title__kk')


class ExamSubjectForm(forms.ModelForm):
    file = forms.FileField(required=False, help_text="Upload an Excel file to create questions.")

    class Meta:
        model = EntranceExamSubject
        fields = '__all__'

    def save(self, commit=True):
        exam_subject = super().save(commit=False)

        if exam_subject.exam_per_day and exam_subject.exam_per_day.pk is None:
            exam_subject.exam_per_day.save()

        if exam_subject.pk is None:
            exam_subject.save()

        file = self.cleaned_data.get('file')
        if file:
            self.validate_and_process_file(file, exam_subject)

        if commit:
            exam_subject.save()

        return exam_subject

    def validate_and_process_file(self, file, exam_subject):
        try:
            df = pd.read_excel(file)
        except Exception as e:
            raise ValidationError(f"Error reading Excel file: {e}")
        self.process_file(df, exam_subject)

    def process_file(self, df, exam_subject):

        for _, row in df.iterrows():
            kk_correct_answers = regex_options(str(row['kk_correct_answers']))
            ru_correct_answers = regex_options(str(row['ru_correct_answers']))
            ru_answers = regex_options(str(row['ru_answers'])) if row['ru_answers'] == row['ru_answers'] else None
            kk_answers = regex_options(str(row['kk_answers'])) if row['kk_answers'] == row['kk_answers'] else None
            open_answer = row.get('open_answer', None)

            question = ExamQuestion.objects.create(
                title={"kk": row['kk_task'], "ru": row['ru_task']},
                explanation_answer={"kk": row['kk_explanation'], "ru": row['ru_explanation']},
                assessment_subject=exam_subject,
                score=row.get('score', 1)
            )
            if open_answer is not None:
                answers = open_answer.split('\n')
                question.type = QuestionType.open_answer
                for answer in answers:
                    wol_answer = remove_latex_bracket(answer)
                    ExamAnswerOption.objects.create(
                        text={"kk": wol_answer, "ru": wol_answer},
                        is_correct=True,
                        question=question
                    )
                question.save(update_fields=['type'])

            if not (kk_answers and ru_answers) and (kk_correct_answers and ru_correct_answers):
                for kk_answer, ru_answer in zip(kk_correct_answers, ru_correct_answers):
                    ExamAnswerOption.objects.create(
                        text={"kk": remove_latex_bracket(kk_answer), "ru": remove_latex_bracket(ru_answer)},
                        is_correct=True,
                        exam_question=question
                    )
            else:
                for kk_answer, ru_answer in zip(kk_answers, ru_answers):
                    is_correct = kk_answer in kk_correct_answers or ru_answer in ru_correct_answers
                    ExamAnswerOption.objects.create(
                        text={"kk": remove_latex_bracket(kk_answer), "ru": remove_latex_bracket(ru_answer)},
                        is_correct=is_correct,
                        exam_question=question
                    )


@admin.register(EntranceExamSubject)
class ExamSubjectAdmin(LocalizedFieldsAdminMixin, admin.ModelAdmin):
    inlines = [ExamQuestionInline]
    search_fields = ('title__ru', 'title__kk')
    list_filter = ('exam_per_day__exam',)
    form = ExamSubjectForm


@admin.register(ExamQuestion)
class ExamQuestionAdmin(LocalizedFieldsAdminMixin, admin.ModelAdmin):
    inlines = [ExamAnswerOptionInline]
    search_fields = ('title__ru', 'title__kk')
    list_filter = ('assessment_subject',)


class DiagnosticExamForm(forms.ModelForm):
    file = forms.FileField(required=False, help_text="Upload an Excel file to create questions.")

    class Meta:
        model = DiagnosticExam
        fields = '__all__'

    def save(self, commit=True):
        diagnostic_exam = super().save(commit=False)

        if diagnostic_exam.pk is None:
            diagnostic_exam.save()

        file = self.cleaned_data.get('file')
        if file:
            self.validate_and_process_file(file, diagnostic_exam)

        if commit:
            diagnostic_exam.save()

        return diagnostic_exam

    def validate_and_process_file(self, file, diagnostic_exam):
        try:
            df = pd.read_excel(file)
        except Exception as e:
            raise ValidationError(f"Error reading Excel file: {e}")
        self.process_file(df, diagnostic_exam)

    def process_file(self, df, diagnostic_exam):

        for _, row in df.iterrows():
            kk_correct_answers = regex_options(str(row['kk_correct_answers']))
            ru_correct_answers = regex_options(str(row['ru_correct_answers']))
            ru_answers = regex_options(str(row['ru_answers'])) if row['ru_answers'] == row['ru_answers'] else None
            kk_answers = regex_options(str(row['kk_answers'])) if row['kk_answers'] == row['kk_answers'] else None
            topic_id = row.get('topic_id', None)
            open_answer = row.get('open_answer', None)

            if topic_id:
                topic = Topic.objects.get(pk=topic_id)
                if not topic:
                    topic_id = None
            question = DiagnosticExamQuestion.objects.create(
                title={"kk": row['kk_task'], "ru": row['ru_task']},
                diagnostic_exam=diagnostic_exam,
                type=str(row['type']),
                score=row.get('score', 1),
                topic_id=topic_id,
                grade=str(row.get('grade', 5))
            )
            if open_answer is not None:
                answers = open_answer.split('\n')
                question.type = QuestionType.open_answer
                for answer in answers:
                    wol_answer = remove_latex_bracket(answer)
                    DiagnosticExamAnswerOption.objects.create(
                        text={"kk": wol_answer, "ru": wol_answer},
                        is_correct=True,
                        question=question
                    )
                question.save(update_fields=['type'])

            if not (kk_answers and ru_answers) and (kk_correct_answers and ru_correct_answers):
                for kk_answer, ru_answer in zip(kk_correct_answers, ru_correct_answers):
                    DiagnosticExamAnswerOption.objects.create(
                        text={"kk": remove_latex_bracket(kk_answer), "ru": remove_latex_bracket(ru_answer)},
                        is_correct=True,
                        diagnostic_exam_question=question
                    )
            else:
                for kk_answer, ru_answer in zip(kk_answers, ru_answers):
                    is_correct = kk_answer in kk_correct_answers or ru_answer in ru_correct_answers
                    DiagnosticExamAnswerOption.objects.create(
                        text={"kk": remove_latex_bracket(kk_answer), "ru": remove_latex_bracket(ru_answer)},
                        is_correct=is_correct,
                        diagnostic_exam_question=question
                    )


class DiagnosticExamQuestionInline(admin.StackedInline):
    model = DiagnosticExamQuestion
    extra = 0


class DiagnosticExamAnswerOptionInline(admin.StackedInline):
    model = DiagnosticExamAnswerOption
    extra = 0


@admin.register(DiagnosticExam)
class DiagnosticExamAdmin(LocalizedFieldsAdminMixin, admin.ModelAdmin):
    list_display = ('title', 'enabled', 'questions_amount', 'duration')
    search_fields = ('title',)
    list_filter = ('enabled',)
    form = DiagnosticExamForm
    inlines = [DiagnosticExamQuestionInline]

    def get_queryset(self, request):
        return super().get_queryset(request)


@admin.register(DiagnosticExamQuestion)
class DiagnosticExamQuestionAdmin(LocalizedFieldsAdminMixin, admin.ModelAdmin):
    list_display = ('title', 'score')
    search_fields = ('title',)
    list_filter = ('score',)
    inlines = [DiagnosticExamAnswerOptionInline]
