import math
import pandas as pd
from django import forms
from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline
from django.core.exceptions import ValidationError
from localized_fields.admin import LocalizedFieldsAdminMixin
from adminsortable2.admin import SortableAdminMixin, SortableInlineAdminMixin
from apps.analytics.admin import QuizInline, ExamInline
from apps.analytics.models import Quiz, Question, QuestionType, AnswerOption
from apps.common.admin import ReadOnlyMixin
from apps.content.models import *


class TopicAdminForm(forms.ModelForm):
    file = forms.FileField(required=False, help_text="Upload an Excel file to create questions.")

    class Meta:
        model = Topic
        fields = '__all__'

    def save(self, commit=True):
        topic = super().save(commit=False)

        # Save the Chapter instance if it's new and not yet saved
        if topic.chapter and topic.chapter.pk is None:
            topic.chapter.save()

        # Save the Topic instance if it has no PK
        if topic.pk is None:
            topic.save()

        file = self.cleaned_data.get('file')

        if file:
            self.validate_and_process_file(file, topic)

        # Save the Topic instance again after processing, if commit=True
        if commit:
            topic.save()

        return topic

    def validate_and_process_file(self, file, topic):
        try:
            df = pd.read_excel(file)
        except Exception as e:
            raise ValidationError(f"Error reading Excel file: {e}")

        required_columns = [
            'kk_task', 'ru_task', 'image_for_task',
            'kk_answers', 'ru_answers', 'kk_correct_answers',
            'ru_correct_answers', 'kk_explanation', 'ru_explanation',
            'video_url'
        ]

        # Check if all required columns are present
        # missing_columns = [col for col in required_columns if col not in df.columns]
        # if missing_columns:
        #     raise ValidationError(f"Missing columns in the uploaded file: {', '.join(missing_columns)}")

        # Further validation: Check for required fields
        # if df[required_columns].isnull().any().any():
        #     raise ValidationError("There are missing values in the required columns.")

        # Additional validation logic if needed
        # for index, row in df.iterrows():
        #     kk_answers = row['kk_answers'].split('\n')
        #     ru_answers = row['ru_answers'].split('\n')
        #     kk_correct_answers = row['kk_correct_answers'].split('\n')
        #     ru_correct_answers = row['ru_correct_answers'].split('\n')
        #
        #     if not set(kk_correct_answers).issubset(set(kk_answers)):
        #         raise ValidationError(f"Row {index + 1}: Some KK correct answers are not present in the KK answers.")
        #
        #     if not set(ru_correct_answers).issubset(set(ru_answers)):
        #         raise ValidationError(f"Row {index + 1}: Some RU correct answers are not present in the RU answers.")

        # If all validations pass, proceed to process the file
        self.process_file(df, topic)

    def process_file(self, df, topic):
        quiz = Quiz.objects.create(topic=topic)
        for _, row in df.iterrows():

            print(row)
            print(bool(row['kk_answers']))
            kk_correct_answers = str(row['kk_correct_answers']).split('\n')
            ru_correct_answers = str(row['ru_correct_answers']).split('\n')
            kk_answers = row['kk_answers'].split('\n') if row['kk_answers'] == row['kk_answers'] else None
            ru_answers = row['ru_answers'].split('\n') if row['ru_answers'] == row['ru_answers'] else None
            explain_video_url = row['video_url'] if row['video_url'] == row['video_url'] else None

            question = Question.objects.create(
                title={"kk": row['kk_task'], "ru": row['ru_task']},
                # image={"kk": row['image_for_task']},
                explanation_answer={"kk": row['kk_explanation'], "ru": row['ru_explanation']},
                explain_video={"kk": explain_video_url},
                quiz=quiz,
                type=QuestionType.multiple_choice if len(kk_correct_answers) > 1 or len(ru_correct_answers) > 1 else QuestionType.one_choice
            )

            print('2222')
            if not (kk_answers and ru_answers) and (kk_correct_answers and ru_correct_answers):
                for kk_answer, ru_answer in zip(kk_correct_answers, ru_correct_answers):
                    AnswerOption.objects.create(
                        text={"kk": kk_answer, "ru": ru_answer},
                        is_correct=True,
                        question=question
                    )
            else:
                for kk_answer, ru_answer in zip(kk_answers, ru_answers):
                    is_correct = kk_answer in kk_correct_answers or ru_answer in ru_correct_answers
                    AnswerOption.objects.create(
                        text={"kk": kk_answer, "ru": ru_answer},
                        is_correct=is_correct,
                        question=question
                    )


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
    fields = ('id', 'name', 'description', 'image', 'chapter', 'file')
    extra = 0
    form = TopicAdminForm


@admin.register(School)
class SchoolAdmin(LocalizedFieldsAdminMixin, admin.ModelAdmin):
    list_display = ('id', 'name', 'priority')
    search_fields = ['name_ru', 'name_kk']


@admin.register(Direction)
class DirectionAdmin(LocalizedFieldsAdminMixin, admin.ModelAdmin):
    list_display = ('id', 'name', 'description', 'image', 'priority')
    search_fields = ['name_ru', 'name_kk']
    list_editable = ('priority',)
    inlines = [SubjectInline, ExamInline]


@admin.register(Subject)
class SubjectAdmin(LocalizedFieldsAdminMixin, admin.ModelAdmin):
    list_display = ('id', 'name', 'direction', 'priority')
    search_fields = ['name_ru', 'name_kk']
    list_filter = ('direction',)
    list_editable = ('priority',)
    inlines = [CourseInline, QuizInline]


@admin.register(Course)
class CourseAdmin(LocalizedFieldsAdminMixin, admin.ModelAdmin):
    list_display = ('id', 'name', 'subject', 'grade', 'priority')
    search_fields = ['name_ru', 'name_kk']
    list_filter = ('subject',)
    list_editable = ('priority',)
    inlines = [QuizInline]


@admin.register(Chapter)
class ChapterAdmin(LocalizedFieldsAdminMixin, admin.ModelAdmin):
    list_display = ('id', 'name', 'quarter', 'course', 'priority')
    search_fields = ['name_ru', 'name_kk']
    list_editable = ('priority',)
    inlines = [TopicInline]


@admin.register(Topic)
class TopicAdmin(LocalizedFieldsAdminMixin, admin.ModelAdmin):
    list_display = ('id', 'name', 'description', 'chapter', 'priority')
    list_editable = ('priority',)
    search_fields = ['name_ru', 'name_kk']
    list_filter = ['chapter']
    form = TopicAdminForm
    inlines = [QuizInline]

