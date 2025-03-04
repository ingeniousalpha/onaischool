import uuid
from collections import defaultdict
from itertools import groupby

from django.db.models import Q
from rest_framework import serializers
from django.utils import timezone

from apps.analytics.exceptions import InvalidAssessmentInput
from apps.analytics.models import Quiz, Question, AnswerOption, EntranceExam, EntranceExamSubject, ExamQuestion, \
    ExamAnswerOption, EntranceExamPerDay, QuestionType, DiagnosticExam, DiagnosticExamQuestion
from apps.common.mixins import UserPropertyMixin
from apps.common.pagination import PaginationForQuestions
from apps.common.serializers import AbstractImageSerializer, AbstractTitleSerializer, AbstractNameSerializer
from apps.content.models import Subject, Chapter, Course
from apps.content.serializers import SubjectSerializer
from apps.users.models import UserExamQuestion, UserExamResult, UserQuizQuestion, UserAssessment, UserAssessmentResult, \
    UserDiagnosticsResult


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
            uqr_id = self.context.get('uqr_id')
            return obj.user_exam_questions.filter(user=user, exam_result_id=uqr_id).exists()

    def get_text(self, obj):
        return obj.text.translate()


class ExamQuestionSerializer(AbstractTitleSerializer, AbstractImageSerializer, UserPropertyMixin):
    options = serializers.SerializerMethodField()
    open_answer = serializers.SerializerMethodField()
    explanation_answer = serializers.SerializerMethodField()
    explanation_answer_image = serializers.SerializerMethodField()
    explanation_correct_answer = serializers.SerializerMethodField()

    class Meta:
        model = ExamQuestion
        fields = [
            'id',
            'title',
            'type',
            'image',
            'options',
            'open_answer',
            'explanation_answer',
            'explanation_answer_image',
            'explanation_correct_answer'
        ]

    def get_options(self, obj):
        if obj.type == QuestionType.open_answer:
            return []
        return ExamQuestionOptionSerializer(obj.exam_answer_options, many=True, context=self.context).data

    def get_open_answer(self, obj):
        user = self.user
        if obj.type == QuestionType.open_answer and obj.user_exam_questions.filter(user=user).exists():
            uqq = obj.user_exam_questions.filter(user=user).order_by('-id').first()
            return {
                "is_correct": uqq.is_correct,
                "user_answer": uqq.user_answer,
            }
        return {}

    def get_explanation_answer(self, obj: Question) -> str:
        return obj.explanation_answer.translate()

    def get_explanation_answer_image(self, obj):
        request = self.context.get('request')
        if obj.explanation_answer_image.translate():
            return request.build_absolute_uri(obj.explanation_answer_image.translate().url)
        return ''

    def get_explanation_correct_answer(self, obj):
        if obj.exam_answer_options.filter(is_correct=True).exists():
            correct_answer = obj.exam_answer_options.filter(is_correct=True).first()
            return correct_answer.text.translate()


class ExamSubjectDetailSerializer(ExamSubjectSerializer):
    questions = serializers.SerializerMethodField()

    class Meta(ExamSubjectSerializer.Meta):
        fields = ExamSubjectSerializer.Meta.fields + ['questions']

    def get_questions(self, obj):
        request = self.context.get('request')
        user = request.user
        paginator = PaginationForQuestions()
        uqr_id = self.context.get('uqr')
        user_exam_questions = user.user_exam_questions.filter(
            exam_question_id__in=obj.exam_questions.values_list('id', flat=True), exam_result_id=uqr_id)
        if user_exam_questions.count() > 0 and user_exam_questions.count() == obj.questions_amount:
            questions = [uqq.exam_question.id for uqq in user_exam_questions]
        else:
            questions_to_create = obj.exam_questions.exclude(
                id__in=user_exam_questions.values_list('exam_question_id', flat=True))[
                                  :obj.questions_amount - user_exam_questions.count()]
            for question in questions_to_create:
                UserExamQuestion.objects.get_or_create(
                    exam_question_id=question.id,
                    user=user,
                    exam_result_id=uqr_id
                )
            questions = (list(user_exam_questions.values_list('exam_question', flat=True)) +
                         list(questions_to_create.values_list('id', flat=True)))
        paginated_data = paginator.paginate_queryset(
            request=request,
            queryset=obj.exam_questions.filter(id__in=questions),
        )
        self.context['uqr_id'] = uqr_id
        serializer = ExamQuestionSerializer(paginated_data, many=True, context=self.context)
        result = paginator.get_paginated_response(serializer.data)
        return result


class ExamPerDayForMainPageSerializer(AbstractTitleSerializer):
    subjects = serializers.SerializerMethodField()
    direction_name = serializers.SerializerMethodField()
    entrance_exam_id = serializers.IntegerField(source="exam.id")
    duration = serializers.SerializerMethodField()

    class Meta:
        model = EntranceExamPerDay
        fields = ['id', 'entrance_exam_id', 'title', 'duration', 'subjects', 'direction_name']

    def get_duration(self, obj):
        return obj.duration * 60

    def get_subjects(self, obj):
        return ExamSubjectSerializer(obj.exam_subjects, many=True).data

    def get_direction_name(self, obj):
        return obj.exam.direction.name.translate()


class ExamPerDaySerializer(AbstractTitleSerializer):
    subjects = serializers.SerializerMethodField()
    duration = serializers.SerializerMethodField()

    class Meta:
        model = EntranceExamPerDay
        fields = ['id', 'title', 'duration', 'subjects']

    def get_duration(self, obj):
        return obj.duration * 60

    def get_subjects(self, obj):
        return ExamSubjectSerializer(obj.exam_subjects, many=True, context=self.context).data


class ExamPerDayDetailSerializer(ExamPerDaySerializer):
    subjects = serializers.SerializerMethodField()

    class Meta(ExamPerDaySerializer.Meta):
        model = EntranceExamPerDay
        fields = ExamPerDaySerializer.Meta.fields + ['subjects']

    def get_subjects(self, obj):
        return ExamSubjectDetailSerializer(obj.exam_subjects, many=True, context=self.context).data


class UserExamResultSerializer(serializers.ModelSerializer):
    exam_per_day = serializers.SerializerMethodField()

    class Meta:
        model = UserExamResult
        fields = ['uuid', 'correct_score', 'exam_per_day']

    def get_exam_per_day(self, obj):
        self.context['uqr'] = obj
        return ExamPerDayDetailSerializer(obj.exam_per_day, many=False, context=self.context).data


class EntranceExamSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    exam_subjects = serializers.SerializerMethodField()

    class Meta:
        model = EntranceExam
        fields = ['id', 'name', 'exam_subjects']

    def get_name(self, obj):
        if obj.direction:
            return obj.direction.name.translate()
        return ''

    def get_exam_subjects(self, obj):
        return ExamPerDaySerializer(obj.exam_per_day.all(), many=True, context=self.context).data


class ExtranceExamDetailSerializer(EntranceExamSerializer):
    next_subjects = serializers.SerializerMethodField()
    passed_duration = serializers.SerializerMethodField()
    uuid = serializers.SerializerMethodField()

    class Meta(EntranceExamSerializer.Meta):
        model = EntranceExam
        fields = EntranceExamSerializer.Meta.fields + ['next_subjects', 'passed_duration', 'uuid']

    def get_uuid(self, obj):
        request = self.context.get('request')
        user = request.user
        query_params = request.query_params
        day = query_params.get('day')
        exam_per_day = EntranceExamPerDay.objects.filter(id=day).first()
        uer = obj.user_exam_results.filter(user=user, exam_per_day=exam_per_day, end_datetime__isnull=True)
        if uer.exists():
            return uer.order_by('-id').first().uuid

    def get_passed_duration(self, obj):
        request = self.context.get('request')
        user = request.user
        query_params = request.query_params
        day = query_params.get('day')
        exam_per_day = EntranceExamPerDay.objects.filter(id=day).first()
        if obj.user_exam_results.filter(user=user, exam_per_day=exam_per_day, end_datetime__isnull=True).exists():
            ueq = obj.user_exam_results.filter(user=user, exam_per_day=exam_per_day, end_datetime__isnull=True).order_by('-id').first()
            if ueq.updated_at < ueq.start_datetime:
                return 0
            passed_duration = ueq.updated_at - ueq.start_datetime
            return passed_duration.total_seconds()

    def get_exam_subjects(self, obj):
        request = self.context.get('request')
        user = request.user
        query_params = request.query_params
        day = query_params.get('day')
        exam_per_day = EntranceExamPerDay.objects.filter(id=day).first()
        user.current_exam_per_day = exam_per_day
        uqr = obj.user_exam_results.filter(Q(user=user) & Q(exam_per_day=exam_per_day) & Q(end_datetime__isnull=True))
        if not uqr.exists():
            UserExamResult.objects.create(user=user,
                                          exam_per_day=exam_per_day,
                                          entrance_exam=obj,
                                          start_datetime=timezone.now())
        else:
            uqr.order_by('-id').first().updated_at = timezone.now()
            uqr.order_by('-id').first().save(update_fields=['updated_at'])
        user.save(update_fields=['current_exam_per_day'])
        self.context['uqr'] = uqr.order_by('-id').first().id
        return ExamPerDayDetailSerializer(obj.exam_per_day.filter(id=day).all(), many=True, context=self.context).data

    def get_next_subjects(self, obj):
        request = self.context.get('request')
        user = request.user
        exam_per_days = obj.exam_per_day.exclude(id__in=user.user_exam_results.values_list('exam_per_day', flat=True))
        return ExamPerDaySerializer(exam_per_days, many=True, context=self.context).data


class AnswersSerializer(AbstractImageSerializer, UserPropertyMixin):
    text = serializers.SerializerMethodField()
    selected = serializers.SerializerMethodField()

    class Meta:
        model = AnswerOption
        fields = ['id', 'text', 'image', 'selected', 'is_correct']

    def get_text(self, obj):
        return obj.text.translate()

    def get_selected(self, obj):
        user = self.user

        if user.is_authenticated:
            question = obj.question
            user_quiz_question = question.user_quiz_questions.filter(
                Q(user=self.user) & Q(report__finished=False)).first()
            if user_quiz_question:
                report_id = user_quiz_question.report.id
                return obj.user_quiz_questions.filter(Q(user=user) & Q(report_id=report_id)).exists()
        return False


class AssessmentAnswerSerializer(AnswersSerializer):
    class Meta(AnswersSerializer.Meta):
        fields = AnswersSerializer.Meta.fields

    def get_selected(self, obj):
        user = self.user
        if user.is_authenticated:
            question = obj.question
            user_assessment_question = question.user_assessment_results.filter(
                Q(user=self.user) & Q(assessment__is_finished=False)).first()
            if user_assessment_question:
                assessment_id = user_assessment_question.assessment.id
                return obj.user_assessment_results.filter(Q(user=user) & Q(assessment_id=assessment_id)).exists()
        return False


class QuizQuestionsSerializer(AbstractTitleSerializer, AbstractImageSerializer, UserPropertyMixin):
    explain_video = serializers.SerializerMethodField()
    answers = serializers.SerializerMethodField()
    is_selected = serializers.SerializerMethodField()
    open_answer = serializers.SerializerMethodField()
    is_answer_viewed = serializers.SerializerMethodField()
    show_report = serializers.SerializerMethodField()
    final_result = serializers.SerializerMethodField()

    class Meta:
        model = Question
        fields = [
            'id', 'title', 'image', 'explain_video',
            'type', 'is_selected', 'answers', 'open_answer',
            'is_answer_viewed', 'show_report', 'final_result'
        ]

    def get_final_result(self, obj):
        if self.user.user_quiz_questions:
            user_question = self.user.user_quiz_questions.filter(question_id=obj.id, report__finished=False).first()
            return False if user_question.is_correct is None else user_question.is_correct
        return False

    def get_explain_video(self, obj):
        return obj.explain_video.translate()

    def get_answers(self, obj):
        if obj.type == QuestionType.open_answer:
            return []
        return AnswersSerializer(obj.answer_options, many=True, context=self.context).data

    def get_is_selected(self, obj):
        user_quiz_question = obj.user_quiz_questions.filter(user=self.user).order_by('-id').first()
        if user_quiz_question is not None:
            if not user_quiz_question.report.finished and user_quiz_question.is_correct is not None:
                return True
        return False

    def get_is_answer_viewed(self, obj):
        uqq = obj.user_quiz_questions.filter(user=self.user).order_by('-id').first()
        if uqq:
            if not uqq.report.finished and uqq.answer_viewed:
                return True
        return False

    def get_show_report(self, obj):
        uqq = obj.user_quiz_questions.filter(user=self.user).first()
        user_questions = UserQuizQuestion.objects.filter(user=self.user, quiz=uqq.quiz, report__finished=False, report_id=uqq.report_id)
        if user_questions.count() >= user_questions.filter(is_correct__isnull=False).count():
            return True
        return False

    def get_open_answer(self, obj):
        user = self.user
        if obj.type == QuestionType.open_answer and obj.user_quiz_questions.filter(user=user).exists():
            uqq = obj.user_quiz_questions.filter(user=user).order_by('-id').first()
            return {
                "is_correct": uqq.is_correct,
                "user_answer": uqq.user_answer,
            }
        return {}


class AssessmentQuestionSerializer(AbstractImageSerializer, AbstractTitleSerializer, UserPropertyMixin):
    answers = serializers.SerializerMethodField()
    is_selected = serializers.SerializerMethodField()
    open_answer = serializers.SerializerMethodField()
    show_report = serializers.SerializerMethodField()
    final_result = serializers.SerializerMethodField()

    class Meta:
        model = Question
        fields = [
            'id', 'title', 'image',
            'type', 'is_selected', 'answers', 'open_answer',
            'show_report', 'final_result'
        ]

    def get_final_result(self, obj):
        if self.user.user_assessment_results:
            user_question = self.user.user_assessment_results.filter(question_id=obj.id,
                                                                     assessment__is_finished=False).first()
            return False if user_question.is_correct is None else user_question.is_correct
        return False

    def get_answers(self, obj):
        if obj.type == QuestionType.open_answer:
            return []
        return AssessmentAnswerSerializer(obj.answer_options, many=True, context=self.context).data

    def get_is_selected(self, obj):
        if obj.user_assessment_results.filter(Q(user=self.user) & Q(question_id=obj.id)).first().is_correct is not None:
            return True
        return False

    def get_show_report(self, obj):
        user_questions = UserAssessmentResult.objects.filter(user=self.user, assessment__is_finished=False)
        if user_questions.count() == user_questions.filter(is_correct__isnull=False).count():
            return True
        return False

    def get_open_answer(self, obj):
        user = self.user
        if obj.type == QuestionType.open_answer and obj.user_assessment_results.filter(user=user).exists():
            uqq = obj.user_assessment_results.filter(user=user).first()
            return {
                "is_correct": uqq.is_correct,
                "user_answer": uqq.user_answer,
            }
        return {}


class AssessmentSerializer(serializers.ModelSerializer):
    passed_duration = serializers.SerializerMethodField()
    questions = AssessmentQuestionSerializer(many=True)
    duration = serializers.SerializerMethodField()

    class Meta:
        model = UserAssessment
        fields = ['id', 'questions', 'passed_duration', 'duration']

    def get_duration(self, obj):
        duration = 60
        if obj.assessment_type == 'SOR':
            duration = duration * obj.subject.sor_duration
        else:
            duration = duration * obj.subject.soch_duration
        return duration

    def get_passed_duration(self, obj):
        if obj.updated_at < obj.start_datetime:
            return 0
        passed_duration = obj.updated_at - obj.start_datetime
        return round(passed_duration.total_seconds(), 2)


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


class QuestionSerializerWithHints(QuizQuestionsSerializer):
    class Meta(QuizQuestionsSerializer.Meta):
        model = Question
        fields = QuizQuestionsSerializer.Meta.fields


class QuestionSerializerWithAnswer(QuizQuestionsSerializer):
    explanation_answer = serializers.SerializerMethodField()
    explanation_answer_image = serializers.SerializerMethodField()
    explanation_correct_answer = serializers.SerializerMethodField()

    class Meta(QuizQuestionsSerializer.Meta):
        model = Question
        fields = QuizQuestionsSerializer.Meta.fields + ['explanation_answer', 'explanation_answer_image',
                                                        'explanation_correct_answer']

    def get_explanation_answer(self, obj: Question) -> str:
        return obj.explanation_answer.translate()

    def get_explanation_answer_image(self, obj):
        request = self.context.get('request')
        if obj.explanation_answer_image.translate():
            return request.build_absolute_uri(obj.explanation_answer_image.translate().url)
        return ''

    def get_explanation_correct_answer(self, obj):
        correct_answers = obj.answer_options.filter(is_correct=True).all()
        correct_answer_text = ''
        for correct_answer in correct_answers:
            correct_answer_text += correct_answer.text.translate() + ' '
            return correct_answer_text.strip()


class QuizSerializer(serializers.ModelSerializer):
    questions = serializers.SerializerMethodField()

    class Meta:
        model = Quiz
        fields = ['id', 'questions', 'questions_amount']

    def get_questions(self, obj):
        return QuizQuestionsSerializer(obj.questions, many=True, context=self.context).data


class CheckAnswerSerializer(serializers.Serializer):
    question_id = serializers.IntegerField()
    answer = serializers.CharField(required=False)
    options = serializers.ListSerializer(child=serializers.IntegerField(required=False), required=False)


class FinishExamSerializer(serializers.Serializer):
    exam_id = serializers.IntegerField()
    day = serializers.IntegerField()


class SubjectAssessmentSerializer(AbstractNameSerializer):
    chapters = serializers.SerializerMethodField()
    courses = serializers.SerializerMethodField()

    class Meta:
        model = Subject
        fields = ['id', 'name', 'chapters', 'courses']

    def get_chapters(self, obj):
        return []

    def get_courses(self, obj):
        return []


class GroupedAssessmentSerializer(serializers.Serializer):
    assessment_type = serializers.CharField()
    subjects = serializers.SerializerMethodField()


class AssessmentSubjectsSerializer(serializers.Serializer):
    subjects = serializers.SerializerMethodField()

    def get_subjects(self, obj):
        return SubjectSerializer(Subject.objects.filter(enable_sor_soch=True).all(), many=True,
                                 context=self.context).data


class AssessmentCreateSerializer(serializers.ModelSerializer, UserPropertyMixin):
    subject_id = serializers.PrimaryKeyRelatedField(queryset=Subject.objects.all())
    chapter_id = serializers.PrimaryKeyRelatedField(queryset=Chapter.objects.all(), required=False)
    course_id = serializers.PrimaryKeyRelatedField(queryset=Course.objects.all())

    class Meta:
        model = UserAssessment
        fields = ['user', 'subject_id', 'assessment_type', 'chapter_id', 'quarter', 'level', 'course_id']

    def validate(self, attrs):
        assessment_type = attrs['assessment_type']
        if assessment_type == 'SOR' and not attrs.get('chapter_id'):
            raise InvalidAssessmentInput
        elif assessment_type == 'SOCH' and not attrs.get('quarter'):
            raise InvalidAssessmentInput
        return attrs

    def generate_assessment_questions(self, obj):
        questions_count = obj.subject.sor_question_count
        questions_query = Question.objects.none()
        if obj.assessment_type == 'SOR':
            questions_query = Question.objects.filter(
                quiz__topic__chapter=obj.chapter,
                level=obj.level
            )
        elif obj.assessment_type == 'SOCH':
            questions_query = Question.objects.filter(
                quiz__topic__chapter__quarter=obj.quarter,
                level=obj.level
            )
        return questions_query.prefetch_related('quiz__topic__chapter').order_by('?')[:questions_count]

    def to_representation(self, instance):
        return {
            'id': instance.uuid,
            'questions': AssessmentQuestionSerializer(instance.questions, many=True, context=self.context).data
        }

    def create(self, validated_data):
        instance = UserAssessment.objects.create(user=self.user,
                                                 assessment_type=validated_data['assessment_type'],
                                                 chapter_id=validated_data.get('chapter_id').id if validated_data.get(
                                                     'chapter_id') else None,
                                                 subject_id=validated_data['subject_id'].id,
                                                 quarter=validated_data.get('quarter'),
                                                 start_datetime=timezone.now(),
                                                 level=validated_data['level'],
                                                 course_id=validated_data['course_id'].id)

        questions = self.generate_assessment_questions(instance)
        instance.questions.set(questions)
        user_assessment_results = [
            UserAssessmentResult(user=self.user, assessment=instance, question=question)
            for question in questions
        ]
        UserAssessmentResult.objects.bulk_create(user_assessment_results)

        return instance


class DiagnosticExamAnswerSerializer(AnswersSerializer):
    class Meta(AnswersSerializer.Meta):
        fields = AnswersSerializer.Meta.fields

    def get_selected(self, obj):
        user = self.user
        if user.is_authenticated:
            question = obj.diagnostic_exam_question
            user_diagnostic_question = question.user_diagnostic_results.filter(
                Q(user=self.user))
            if user_diagnostic_question.exists():
                return user_diagnostic_question.filter(answers=obj.id).exists()
        return False


class DiagnosticExamQuestionSerializer(AbstractImageSerializer, AbstractTitleSerializer, UserPropertyMixin):
    answers = serializers.SerializerMethodField()
    is_selected = serializers.SerializerMethodField()
    open_answer = serializers.SerializerMethodField()
    show_report = serializers.SerializerMethodField()
    explain_video = serializers.SerializerMethodField()
    explanation_answer = serializers.SerializerMethodField()
    explanation_answer_image = serializers.SerializerMethodField()
    explanation_correct_answer = serializers.SerializerMethodField()
    final_result = serializers.SerializerMethodField()
    is_answer_viewed = serializers.SerializerMethodField()

    class Meta:
        model = DiagnosticExamQuestion
        fields = [
            'id', 'title', 'image', 'open_answer', 'show_report',
            'final_result', 'is_answer_viewed',
            'type', 'is_selected', 'answers', 'explain_video', 'explanation_answer', 'explanation_answer_image',
            'explanation_correct_answer']

    def get_final_result(self, obj):
        return False

    def get_is_answer_viewed(self, obj):
        return False

    def get_explanation_correct_answer(self, obj):
        return None

    def get_explanation_answer(self, obj):
        return None

    def get_explanation_answer_image(self, obj):
        return None

    def get_explain_video(self, obj):
        return None

    def get_explanation(self, obj):
        return None

    def get_show_report(self, obj):
        user_diagnostic_results = self.user.user_diagnostic_results.filter(user_diagnostic_report__is_finished=False)
        if user_diagnostic_results.exists():
            diagnostic_report = user_diagnostic_results.first().user_diagnostic_report
            user_questions = UserDiagnosticsResult.objects.filter(user=self.user,
                                                                  user_diagnostic_report=diagnostic_report,
                                                                  user_diagnostic_report__is_finished=False)
            if user_questions.count() == user_questions.filter(is_correct__isnull=False).count():
                return True
        return False

    def get_open_answer(self, obj):
        user = self.user
        if obj.type == QuestionType.open_answer and obj.user_diagnostic_results.filter(user=user).exists():
            uqq = obj.user_diagnostic_results.filter(user=user).first()
            return {
                "is_correct": uqq.is_correct,
                "user_answer": uqq.user_answer,
            }
        return {}

    def get_answers(self, obj):
        return DiagnosticExamAnswerSerializer(obj.diagnostic_exam_answer_options, many=True, context=self.context).data

    def get_is_selected(self, obj):
        if not obj.user_diagnostic_results.filter(Q(user=self.user) & Q(question_id=obj.id)).exists():
            return False
        if obj.user_diagnostic_results.filter(Q(user=self.user) & Q(question_id=obj.id)).first().is_correct is not None:
            return True
        return False


class DiagnosticExamSerializer(serializers.ModelSerializer):
    questions = serializers.SerializerMethodField()

    class Meta:
        model = DiagnosticExam
        fields = ['id', 'questions', 'questions_amount']

    def get_questions(self, obj):
        return DiagnosticExamQuestionSerializer(obj.diagnostic_exam_questions, many=True, context=self.context).data
