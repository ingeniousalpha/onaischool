from itertools import groupby

from rest_framework import serializers
from django.utils import timezone

from apps.analytics.models import Quiz, Question, AnswerOption, EntranceExam, EntranceExamSubject, ExamQuestion, \
    ExamAnswerOption, EntranceExamPerDay
from apps.common.pagination import PaginationForQuestions
from apps.common.serializers import AbstractImageSerializer, AbstractTitleSerializer
from apps.users.models import UserExamQuestion, UserExamResult


class ExamSubjectSerializer(AbstractTitleSerializer):
    class Meta:
        model = EntranceExamSubject
        fields = ['id', 'title', 'max_score', 'questions_amount']


class ExamQuestionOptionSerializer(AbstractImageSerializer):
    text = serializers.SerializerMethodField()
    selected = serializers.SerializerMethodField()

    class Meta:
        model = ExamAnswerOption
        fields = ['id', 'text', 'image', 'selected', 'is_correct']

    def get_selected(self, obj):
        user = self.context.get('request').user
        if user.is_authenticated:
            return obj.user_exam_questions.filter(user=user).exists()

    def get_text(self, obj):
        return obj.text.translate()


class ExamQuestionSerializer(AbstractTitleSerializer):
    options = serializers.SerializerMethodField()

    class Meta:
        model = ExamQuestion
        fields = ['id', 'title', 'options']

    def get_options(self, obj):
        return ExamQuestionOptionSerializer(obj.exam_answer_options, many=True, context=self.context).data


class ExamSubjectDetailSerializer(ExamSubjectSerializer):
    questions = serializers.SerializerMethodField()

    class Meta(ExamSubjectSerializer.Meta):
        fields = ExamSubjectSerializer.Meta.fields + ['questions']

    def get_questions(self, obj):
        request = self.context.get('request')
        user = request.user
        paginator = PaginationForQuestions()

        user_exam_questions = user.user_exam_questions.filter(
            exam_question_id__in=obj.exam_questions.values_list('id', flat=True))

        if user_exam_questions.count() == obj.questions_amount:
            questions = [uqq.question for uqq in user_exam_questions]
        else:
            questions_to_create = obj.exam_questions.exclude(
                id__in=user_exam_questions.values_list('exam_question_id', flat=True))[
                                  :obj.questions_amount - user_exam_questions.count()]
            for question in questions_to_create:
                UserExamQuestion.objects.get_or_create(
                    exam_question=question.id,
                    user=user,
                )
            questions = list(user_exam_questions.values_list('exam_question', flat=True)) + list(questions_to_create)

        paginated_data = paginator.paginate_queryset(queryset=obj.exam_questions.filter(id__in=questions), request=request)
        serializer = ExamQuestionSerializer(paginated_data, many=True, context=self.context)
        result = paginator.get_paginated_response(serializer.data)
        return result


class ExamPerDayForMainPageSerializer(AbstractTitleSerializer):
    subjects = serializers.SerializerMethodField()
    entrance_exam_id = serializers.IntegerField(source="exam.id")

    class Meta:
        model = EntranceExamPerDay
        fields = ['id', 'entrance_exam_id', 'title', 'duration', 'subjects']

    def get_subjects(self, obj):
        return ExamSubjectSerializer(obj.exam_subjects, many=True).data


class ExamPerDaySerializer(AbstractTitleSerializer):
    subjects = serializers.SerializerMethodField()

    class Meta:
        model = EntranceExamPerDay
        fields = ['id', 'title', 'duration', 'subjects']

    def get_subjects(self, obj):
        return ExamSubjectSerializer(obj.exam_subjects, many=True).data


class ExamPerDayDetailSerializer(ExamPerDaySerializer):
    subjects = serializers.SerializerMethodField()

    class Meta(ExamPerDaySerializer.Meta):
        model = EntranceExamPerDay
        fields = ExamPerDaySerializer.Meta.fields

    def get_subjects(self, obj):
        return ExamSubjectDetailSerializer(obj.exam_subjects, many=True, context=self.context).data


class EntranceExamSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    exam_subjects = serializers.SerializerMethodField()

    class Meta:
        model = EntranceExam
        fields = ['id', 'name', 'exam_subjects']

    def get_name(self, obj):
        return obj.direction.name.translate()

    def get_exam_subjects(self, obj):
        return ExamPerDaySerializer(obj.exam_per_day.all(), many=True).data


class ExtranceExamDetailSerializer(EntranceExamSerializer):

    class Meta(EntranceExamSerializer.Meta):
        model = EntranceExam
        fields = EntranceExamSerializer.Meta.fields

    def get_exam_subjects(self, obj):
        request = self.context.get('request')
        user = request.user
        if not obj.user_exam_results.filter(user=user):
            UserExamResult.objects.create(user=user,
                                          entrance_exam=obj,
                                          start_datetime=timezone.now())
        query_params = request.query_params
        day = query_params.get('day')

        user.current_exam_per_day = EntranceExamPerDay.objects.filter(id=day).first()
        user.save(update_fields=['current_exam_per_day'])

        return ExamPerDayDetailSerializer(obj.exam_per_day.filter(id=day).all(), many=True, context=self.context).data


class AnswersSerializer(AbstractImageSerializer):
    text = serializers.SerializerMethodField()
    selected = serializers.SerializerMethodField()

    class Meta:
        model = AnswerOption
        fields = ['id', 'text', 'image', 'selected', 'is_correct']

    def get_text(self, obj):
        return obj.text.translate()

    def get_selected(self, obj):
        user = self.context.get('request').user
        if user.is_authenticated:
            return obj.user_quiz_questions.filter(user=user).exists()
        return False


class QuizQuestionsSerializer(AbstractTitleSerializer, AbstractImageSerializer):
    explain_video = serializers.SerializerMethodField()
    answers = serializers.SerializerMethodField()

    class Meta:
        model = Question
        fields = ['id', 'title', 'image', 'explain_video', 'type', 'answers']

    def get_explain_video(self, obj):
        return obj.explain_video.translate()

    def get_answers(self, obj):
        return AnswersSerializer(obj.answer_options, many=True, context=self.context).data


class QuizQuestionDetailSerializer(QuizQuestionsSerializer):
    explanation_answer = serializers.SerializerMethodField()
    explanation_answer_image = serializers.SerializerMethodField()

    class Meta(QuizQuestionsSerializer.Meta):
        model = Question
        fields = QuizQuestionsSerializer.Meta.fields + ['explanation_answer', 'explanation_answer_image']

    def get_explanation_answer(self, obj: Question) -> str:
        return obj.explanation_answer.translate()

    def get_explanation_answer_image(self, obj):
        request = self.context.get('request')
        if obj.explanation_answer_image.translate():
            return request.build_absolute_uri(obj.explanation_answer_image.translate().url)
        return ''


class QuizSerializer(serializers.ModelSerializer):
    questions = serializers.SerializerMethodField()

    class Meta:
        model = Quiz
        fields = ['id', 'questions', 'questions_amount']

    def get_questions(self, obj):
        return QuizQuestionsSerializer(obj.questions, many=True).data


class CheckAnswerSerializer(serializers.Serializer):
    question_id = serializers.IntegerField()
    options = serializers.ListSerializer(child=serializers.IntegerField(required=True))


class EntranceCheckAnswerSerializer(serializers.Serializer):
    question_id = serializers.IntegerField()
    options = serializers.ListSerializer(child=serializers.IntegerField(required=True))


class FinishExamSerializer(serializers.Serializer):
    exam_id = serializers.IntegerField()
    day = serializers.IntegerField()