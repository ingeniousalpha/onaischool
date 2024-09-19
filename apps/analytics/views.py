from django.db.models import Q
from django.shortcuts import render
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ReadOnlyModelViewSet
from django.utils import timezone

from apps.analytics.exceptions import AnswerDoesntExists, ExamNotFound
from apps.analytics.models import Quiz, Question, AnswerOption, EntranceExam, ExamAnswerOption, QuestionType
from apps.analytics.serializers import QuizSerializer, QuizQuestionsSerializer, QuizQuestionDetailSerializer, \
    CheckAnswerSerializer, EntranceExamSerializer, ExtranceExamDetailSerializer, EntranceCheckAnswerSerializer, \
    FinishExamSerializer
from apps.common.mixins import PrivateSONRendererMixin
from apps.users.models import UserQuizQuestion, UserExamQuestion


class EntranceExamView(PrivateSONRendererMixin, ReadOnlyModelViewSet):
    queryset = EntranceExam.objects.all()
    serializer_class = EntranceExamSerializer
    pagination_class = None

    def get_queryset(self):
        return super().get_queryset().filter(direction__isnull=False)

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
            user_quiz_questions = user.user_quiz_questions.filter(question=quiz.id)
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
        user = request.user
        user_quiz_answer = instance.user_quiz_questions.filter(Q(user=user) & Q(question_id=instance.id)).first()
        user_quiz_answer.is_correct = False
        user_quiz_answer.save(update_fields=['is_correct'])
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
        open_answer = serializer_data.get('answer', None)

        if not options and not open_answer:
            return Response({'error': 'No options provided'}, status=400)

        answers = AnswerOption.objects.filter(
            Q(id__in=options,
              question_id=question_id)
            |
            Q(question_id=question_id,
              question__type=QuestionType.open_answer)
        )
        if not answers.exists():
            raise AnswerDoesntExists
        data = []
        uqq = UserQuizQuestion.objects.filter(user=user, question_id=question_id).first()
        if uqq:
            uqq.answers.clear()
        is_correct = True
        correct_answer_count = 0
        for answer in answers:
            is_correct = True
            if answer.question.type == QuestionType.open_answer:
                if not open_answer:
                    is_correct = False

                elif answer.text.ru.lower() == open_answer.lower():
                    uqq.answers.add(answer.id)
                    uqq.is_correct = True
                else:
                    is_correct = False
            else:
                uqq.answers.add(answer.id)
                if not answer.is_correct:
                    is_correct = False
                uqq.updated_at = timezone.now()
                uqq.save(update_fields=['updated_at'])
            data.append({
                    'answer_id': answer.id,
                    'answer_text': open_answer,
                    'is_correct': is_correct,
                    'life_count': 4
            })
            if is_correct:
                correct_answer_count += 1
        if answers.count() == correct_answer_count:
            uqq.is_correct = is_correct
        else:
            uqq.is_correct = False
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


class FinishEntranceExamView(PrivateSONRendererMixin, APIView):
    serializer_class = FinishExamSerializer

    def post(self, request, *args, **kwargs):
        user = request.user
        serializer_data = FinishExamSerializer(request.data).data
        entrance_exam = EntranceExam.objects.filter(id=serializer_data['exam_id']).first()
        if not entrance_exam:
            raise ExamNotFound
        user_exam_result = user.user_exam_results.filter(entrance_exam_id=entrance_exam.id).first()
        if not user_exam_result.end_datetime:
            user_exam_result.end_datetime = timezone.now()
        correct_question_count = 0
        user_exam_questions = user.user_exam_questions.filter(
            Q(entrance_exam_id=entrance_exam.id) and Q(is_correct=True))
        for user_exam_question in user_exam_questions:
            correct_question_count += user_exam_question.exam_question.score
        passing_score = 0
        exam_per_day = entrance_exam.exam_per_day.filter(id=serializer_data['day']).first()
        if exam_per_day:
            passing_score = exam_per_day.passing_score
        user_exam_result.correct_score = correct_question_count
        user_exam_result.save(update_fields=['end_datetime', 'correct_score'])
        duration = user_exam_result.end_datetime - user_exam_result.start_datetime
        duration_seconds = duration.total_seconds()
        duration_minutes = duration_seconds / 60
        resp_data = {
            'score': correct_question_count,
            'duration': round(duration_minutes, 2),
            'passing_score': passing_score,
        }
        return Response(resp_data)
