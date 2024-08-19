from itertools import groupby

from rest_framework import serializers

from apps.analytics.models import Quiz, Question, AnswerOption, EntranceExam, EntranceExamSubject
from apps.common.serializers import AbstractImageSerializer, AbstractTitleSerializer


class ExamSubjectSerializer(AbstractTitleSerializer):

    class Meta:
        model = EntranceExamSubject
        fields = ['id', 'title', 'max_score', 'questions_amount']


class EntranceExamSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    exam_subjects = serializers.SerializerMethodField()

    class Meta:
        model = EntranceExam
        fields = ['id', 'name', 'duration', 'exam_subjects']

    def get_name(self, obj):
        return obj.direction.name.translate()

    def get_exam_subjects(self, obj):
        exam_subjects = obj.exam_subjects.all()
        grouped_by_days = groupby(exam_subjects, key=lambda c: c.day)
        grouped_chapters_data = [
            {
                'day': key,
                'subjects': ExamSubjectSerializer(list(groups), many=True, context=self.context).data
            }
            for key, groups in grouped_by_days
        ]
        return grouped_chapters_data


class ExtranceExamDetailSerializer(EntranceExamSerializer):
    ...


class AnswersSerializer(AbstractImageSerializer):
    text = serializers.SerializerMethodField()
    selected = serializers.SerializerMethodField()

    class Meta:
        model = AnswerOption
        fields = ['id', 'text', 'image', 'selected']

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


