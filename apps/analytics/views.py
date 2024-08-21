from django.db.models import Q
from django.shortcuts import render
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ReadOnlyModelViewSet
from django.utils import timezone

from apps.analytics.exceptions import AnswerDoesntExists
from apps.analytics.models import Quiz, Question, AnswerOption, EntranceExam, ExamAnswerOption
from apps.analytics.serializers import QuizSerializer, QuizQuestionsSerializer, QuizQuestionDetailSerializer, \
    CheckAnswerSerializer, EntranceExamSerializer, ExtranceExamDetailSerializer, EntranceCheckAnswerSerializer
from apps.common.mixins import PrivateSONRendererMixin
from apps.users.models import UserQuizQuestion, UserExamQuestion


class EntranceExamView(PrivateSONRendererMixin, ReadOnlyModelViewSet):
    queryset = EntranceExam.objects.all()
    serializer_class = EntranceExamSerializer
    pagination_class = None

    def get_serializer_class(self):
        if self.action == "retrieve":
            return ExtranceExamDetailSerializer
        return EntranceExamSerializer


class TopicQuizzesView(PrivateSONRendererMixin, ReadOnlyModelViewSet):
    queryset = Question.objects.all()
    serializer_class = QuizQuestionsSerializer
    pagination_class = None

    def get_serializer_class(self):
        if self.action == "retrieve":
            return QuizQuestionDetailSerializer
        return QuizQuestionsSerializer

    def list(self, request, *args, **kwargs):
        queryset = super().get_queryset()

        topic_id = self.request.query_params.get('topic_id')
        subject_id = self.request.query_params.get('subject_id')
        course_id = self.request.query_params.get('course_id')
        user = self.request.user
        filter_conditions = Q()
        if topic_id:
            filter_conditions |= Q(topic_id=topic_id)
        if subject_id:
            filter_conditions |= Q(subject_id=subject_id)
        if course_id:
            filter_conditions |= Q(course_id=course_id)

        quiz = Quiz.objects.filter(filter_conditions).first()
        if quiz:
            user_quiz_questions = user.user_quiz_questions.filter(exam_question=quiz.id)
            if user_quiz_questions.count() == quiz.questions_amount:
                questions = [uqq.question for uqq in user_quiz_questions]
            else:
                questions = queryset.filter(quiz=quiz)[:quiz.questions_amount]
                for question in questions:
                    instance, created = UserQuizQuestion.objects.get_or_create(
                        quiz=question.quiz,
                        user=user,
                        question=question
                    )
            serializer = self.get_serializer(questions,
                                             many=True,
                                             context={"request": request})
            return Response(serializer.data)
        return Response([])

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, context={"request": request})
        return Response(serializer.data)


class CheckAnswerView(PrivateSONRendererMixin, APIView):
    serializer_class = CheckAnswerSerializer

    def post(self, request, *args, **kwargs):
        user = request.user
        serializer = CheckAnswerSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer_data = serializer.validated_data

        options = serializer_data.get('options', [])
        question_id = serializer_data.get('question_id')

        if not options:
            return Response({'error': 'No options provided'}, status=400)

        answers = AnswerOption.objects.filter(
            id__in=options,
            question_id=question_id
        )
        if not answers.exists():
            raise AnswerDoesntExists
        data = []
        is_correct = True
        uqq = UserQuizQuestion.objects.filter(user=user, question_id=question_id).first()
        if uqq:
            uqq.answers.clear()
        for answer in answers:
            uqq.answers.add(answer.id)
            if not answer.is_correct:
                is_correct = False
            uqq.updated_at = timezone.now()
            uqq.save(update_fields=['updated_at'])
            data.append({
                    'answer_id': answer.id,
                    'is_correct': answer.is_correct,
                    'life_count': 4
            })
        uqq.is_correct = is_correct
        uqq.save(update_fields=['is_correct'])
        return Response(data)


class EntranceExamCheckAnswerView(PrivateSONRendererMixin, APIView):
    serializer_class = EntranceCheckAnswerSerializer

    def post(self, request, *args, **kwargs):
        user = request.user
        serializer = EntranceCheckAnswerSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer_data = serializer.validated_data

        options = serializer_data.get('options', [])
        question_id = serializer_data.get('question_id')

        if not options:
            return Response({'error': 'No options provided'}, status=400)

        answers = ExamAnswerOption.objects.filter(
            id__in=options,
            exam_question_id=question_id
        )
        if not answers.exists():
            raise AnswerDoesntExists
        data = []
        is_correct = True
        uqq = UserExamQuestion.objects.filter(user=user, exam_question=question_id).first()
        if uqq:
            uqq.answers.clear()
        for answer in answers:
            uqq.answers.add(answer.id)
            if not answer.is_correct:
                is_correct = False
            uqq.updated_at = timezone.now()
            uqq.save(update_fields=['updated_at'])
            data.append({
                    'answer_id': answer.id,
                    'is_correct': answer.is_correct,
                    'life_count': 4
            })
        uqq.is_correct = is_correct
        uqq.save(update_fields=['is_correct'])
        return Response(data)

