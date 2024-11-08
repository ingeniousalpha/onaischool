from django.db.models import Q
from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ReadOnlyModelViewSet, GenericViewSet
from django.utils import timezone

from apps.analytics.exceptions import AnswerDoesntExists, ExamNotFound, QuestionNotFound, YouCannotFinishQuiz
from apps.analytics.models import Quiz, Question, AnswerOption, EntranceExam, ExamAnswerOption, QuestionType, \
    DiagnosticExam, DiagnosticExamAnswerOption
from apps.analytics.serializers import QuizSerializer, QuizQuestionsSerializer, QuizQuestionDetailSerializer, \
    CheckAnswerSerializer, EntranceExamSerializer, ExtranceExamDetailSerializer, \
    FinishExamSerializer, QuestionSerializerWithHints, QuestionSerializerWithAnswer, AssessmentSubjectsSerializer, \
    AssessmentCreateSerializer, AssessmentQuestionSerializer, DiagnosticExamSerializer, \
    DiagnosticExamQuestionSerializer, AssessmentSerializer
from apps.common.mixins import PrivateSONRendererMixin
from apps.content.models import Subject
from apps.content.serializers import SubjectSerializer, TopicSerializer
from apps.users.models import UserQuizQuestion, UserExamQuestion, UserQuizReport, UserAssessmentResult, UserAssessment, \
    UserDiagnosticsResult, UserDiagnosticExamReport, MyTopic


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


class DiagnosticExamQuestionView(PrivateSONRendererMixin, ReadOnlyModelViewSet):
    queryset = DiagnosticExam.objects.all()
    serializer_class = DiagnosticExamSerializer
    pagination_class = None

    def get_queryset(self):
        return super().get_queryset()

    def get_serializer_class(self):
        if self.action == "retrieve":
            return DiagnosticExamQuestionSerializer
        return DiagnosticExamSerializer

    def retrieve(self, request, *args, **kwargs):
        diagnostic_exam = self.get_object()
        if not diagnostic_exam:
            raise ExamNotFound

        user = self.request.user
        user_diagnostic_report = user.user_diagnostic_reports.filter(
            diagnostic_exam=diagnostic_exam, is_finished=False
        ).prefetch_related('questions').prefetch_related('user_diagnostic_results')

        if user_diagnostic_report.exists():
            user_diagnostic_report = user_diagnostic_report.first()
        else:
            user_diagnostic_report = UserDiagnosticExamReport.objects.create(user=user, diagnostic_exam=diagnostic_exam)

        questions = user_diagnostic_report.questions.all().order_by('id')

        if not questions.exists():
            diagnostic_questions = diagnostic_exam.diagnostic_exam_questions.all()[:diagnostic_exam.questions_amount]
            user_diagnostic_report.questions.add(*diagnostic_questions)
            questions = user_diagnostic_report.questions.order_by('id')

        user_diagnostic_results = user.user_diagnostic_results.filter(user_diagnostic_report=user_diagnostic_report)
        if questions.count() != user_diagnostic_results.count():
            missing_questions = user_diagnostic_report.questions.exclude(
                id__in=user_diagnostic_results.values('question_id'))
            for question in missing_questions:
                UserDiagnosticsResult.objects.get_or_create(
                    user_diagnostic_report=user_diagnostic_report,
                    user=user,
                    question=question,
                )

        serializer = self.get_serializer(questions, many=True, context={"request": request})
        data = {
            'id': diagnostic_exam.id,
            'uuid': user_diagnostic_report.uuid,
            'questions': serializer.data
        }
        return Response(data)


class DiagnosticExamView(PrivateSONRendererMixin, viewsets.GenericViewSet):
    queryset = UserDiagnosticExamReport.objects.all()
    lookup_field = 'uuid'

    def finish_diagnostic_exam(self, request, *args, **kwargs):
        user_diagnostic_exam = self.get_object()
        user = request.user

        if user_diagnostic_exam.user != user:
            raise YouCannotFinishQuiz

        user_exam_answer = user_diagnostic_exam.user_diagnostic_results.filter(user=user)

        questions_amount = user_diagnostic_exam.diagnostic_exam.questions_amount
        correct_questions = user_exam_answer.filter(is_correct=True).count()
        repeat_topics = set()
        for incorrect_question in user_exam_answer.filter(Q(is_correct=False) | Q(is_correct__isnull=True)).all():
            repeat_topics.add(incorrect_question.question.topic)

        incorrect_questions = questions_amount - correct_questions
        data = {
            'correct_questions': correct_questions,
            'incorrect_questions': incorrect_questions,
            'repeat_topics': TopicSerializer(repeat_topics, many=True, context=self.get_serializer_context()).data
        }
        user_diagnostic_exam.is_finished = True
        user_diagnostic_exam.save(update_fields=['is_finished'])

        return Response(data)

    def repeat_topics(self, request, *args, **kwargs):
        user_diagnostic_exam = self.get_object()
        user = request.user

        if user_diagnostic_exam.user != user:
            raise YouCannotFinishQuiz

        user_exam_answer = user_diagnostic_exam.user_diagnostic_results.filter(user=user)
        repeat_topics = set()
        for incorrect_question in user_exam_answer.filter(Q(is_correct=False) | Q(is_correct__isnull=True)).all():
            repeat_topics.add(incorrect_question.question.topic)

        for topic in repeat_topics:
            quizzes = topic.quizzes.all()
            completed = False
            if quizzes:
                quiz = quizzes.first()
                if quiz:
                    questions_amount = quiz.questions_amount
                    answered_count = user.user_quiz_questions.filter(
                        Q(answers__isnull=False) & Q(quiz_id=quiz.id)).count()
                    completed = (questions_amount == answered_count)
            MyTopic.objects.update_or_create(user=user,
                                             course_id=topic.chapter.course.id,
                                             topic_id=topic.id,
                                             defaults={'is_completed': completed})
        return Response({}, status=status.HTTP_201_CREATED)


class TopicQuizzesView(PrivateSONRendererMixin, ReadOnlyModelViewSet):
    queryset = Question.objects.prefetch_related('user_quiz_questions').select_related('quiz').all()
    serializer_class = QuizQuestionsSerializer
    pagination_class = None

    def get_serializer_class(self):
        if self.action == "retrieve":
            return QuestionSerializerWithAnswer
        return QuestionSerializerWithAnswer

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
            user_quiz_report = user.user_quiz_reports.filter(Q(quiz_id=quiz.id) & Q(finished=False)).first()
            is_repeat = self.request.query_params.get('is_repeat', 'false').lower() == 'true'
            if is_repeat:
                user_quiz_report.finished = True
                user_quiz_report.save()

            if user_quiz_report is None or is_repeat:
                user_quiz_report = UserQuizReport.objects.create(
                    user_id=user.id,
                    quiz_id=quiz.id
                )
            user_quiz_questions = user.user_quiz_questions.filter(Q(quiz_id=quiz.id) & Q(report__finished=False) & Q(report=user_quiz_report))
            if user_quiz_questions.count() == quiz.questions_amount:
                questions = [uqq.question for uqq in user_quiz_questions]
            else:
                questions = queryset.filter(quiz=quiz)[:quiz.questions_amount]
                for question in questions:
                    instance, created = UserQuizQuestion.objects.get_or_create(
                        quiz=question.quiz,
                        user=user,
                        question=question,
                        report=user_quiz_report
                    )
            serializer = self.get_serializer(questions,
                                             many=True,
                                             context={"request": request})

            return Response({'quiz_id': quiz.id,
                             'questions': serializer.data})
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
        uqq = UserQuizQuestion.objects.filter(
            Q(user=user) & Q(question_id=question_id) & Q(report__finished=False)).order_by('-id').first()
        if uqq:
            uqq.answers.clear()
        is_correct = True
        correct_answer_count = 0
        for answer in answers:
            is_correct = True
            if answer.question.type == QuestionType.open_answer:
                uqq.user_answer = open_answer
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
                'user_answer': open_answer,
                'is_correct': is_correct,
                'life_count': 4,
                'show_report': False
            })
            if is_correct:
                correct_answer_count += 1
        if answers.count() == correct_answer_count:
            uqq.is_correct = is_correct
        else:
            uqq.is_correct = False
        uqq.save(update_fields=['is_correct', 'user_answer'])

        user_questions = UserQuizQuestion.objects.filter(user=user, quiz=uqq.quiz, report__finished=False)
        if user_questions.count() == user_questions.filter(is_correct__isnull=False).count():
            for d in data:
                d['show_report'] = True
        return Response(data)


class DiagnosticCheckAnswerView(PrivateSONRendererMixin, APIView):

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

        answers = DiagnosticExamAnswerOption.objects.filter(
            Q(id__in=options,
              diagnostic_exam_question_id=question_id)
            |
            Q(diagnostic_exam_question_id=question_id,
              diagnostic_exam_question__type=QuestionType.open_answer))
        if not answers.exists():
            raise AnswerDoesntExists
        data = []
        uqq = UserDiagnosticsResult.objects.filter(
            Q(user=user) & Q(question_id=question_id)).first()
        if not uqq:
            raise ExamNotFound
        if uqq:
            uqq.answers.clear()
        is_correct = True
        correct_answer_count = 0
        for answer in answers:
            is_correct = True
            if answer.diagnostic_exam_question.type == QuestionType.open_answer:
                uqq.user_answer = open_answer
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
                'user_answer': open_answer,
                'is_correct': is_correct,
                'show_report': False
            })
            if is_correct:
                correct_answer_count += 1
        if answers.count() == correct_answer_count:
            uqq.is_correct = is_correct
        else:
            uqq.is_correct = False
        uqq.save(update_fields=['is_correct', 'user_answer'])
        user_questions = UserDiagnosticsResult.objects.filter(user=user,
                                                              user_diagnostic_report=uqq.user_diagnostic_report,
                                                              user_diagnostic_report__is_finished=False)
        if user_questions.count() == user_questions.filter(is_correct__isnull=False).count():
            for d in data:
                d['show_report'] = True
        return Response(data)


class EntranceExamCheckAnswerView(PrivateSONRendererMixin, APIView):
    serializer_class = CheckAnswerSerializer

    def post(self, request, *args, **kwargs):
        user = request.user
        serializer = CheckAnswerSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer_data = serializer.validated_data

        options = serializer_data.get('options', [])
        question_id = serializer_data.get('question_id')
        open_answer = serializer_data.get('answer', None)

        answers = ExamAnswerOption.objects.filter(
            Q(id__in=options,
              exam_question_id=question_id)
            |
            Q(exam_question_id=question_id,
              exam_question__type=QuestionType.open_answer)
        )
        if not answers.exists():
            raise AnswerDoesntExists
        data = []
        is_correct = True
        uqq = UserExamQuestion.objects.filter(user=user,
                                              exam_question=question_id,
                                              exam_result__end_datetime__isnull=True).order_by('-id').first()
        if uqq.exam_result:
            uqq.exam_result.updated_at = timezone.now()
            uqq.exam_result.save()
        if uqq:
            uqq.answers.clear()
        for answer in answers:
            is_correct = True
            if answer.exam_question.type == QuestionType.open_answer:
                uqq.user_answer = open_answer
                if not open_answer:
                    is_correct = False
                elif answer.text.ru.lower() == open_answer.lower():
                    print(11111)
                    uqq.answers.add(answer.id)
                    uqq.is_correct = True
                else:
                    print('faslse false')
                    is_correct = False
            else:
                uqq.answers.add(answer.id)
                if not answer.is_correct:
                    is_correct = False
                uqq.updated_at = timezone.now()
                uqq.save(update_fields=['updated_at'])
            data.append({
                'answer_id': answer.id,
                'user_answer': open_answer,
                'is_correct': is_correct,
                'life_count': 4
            })
        uqq.is_correct = is_correct
        uqq.save(update_fields=['is_correct', 'user_answer'])
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
        resp_data = {
            'score': correct_question_count,
            'duration': duration_seconds,
            'passing_score': passing_score,
        }
        return Response(resp_data)


class QuizView(PrivateSONRendererMixin,
               viewsets.GenericViewSet,
               viewsets.mixins.ListModelMixin):
    queryset = (Question.objects.
                prefetch_related('user_quiz_questions').
                select_related('quiz').all())

    def get_serializer_class(self):
        actions = {
            'show_hints': QuestionSerializerWithHints,
            'show_answer': QuestionSerializerWithAnswer,
        }
        return actions.get(self.action)

    def show_hints(self, request, pk: int):
        instance = self.get_object()
        user = request.user
        user_quiz_answer = instance.user_quiz_questions.filter(
            Q(user=user) &
            Q(question_id=instance.id)
        ).order_by('-id').first()
        user_quiz_answer.used_hints = True
        user_quiz_answer.save(update_fields=['used_hints'])
        serializer = self.get_serializer(instance, context={"request": request})
        return Response(serializer.data)

    def show_answer(self, request, pk: int):
        instance = self.get_object()
        user = request.user
        user_quiz_answer = instance.user_quiz_questions.filter(
            Q(user=user) &
            Q(question_id=instance.id)
        ).order_by('-id').first()

        if not user_quiz_answer.is_correct:
            user_quiz_answer.is_correct = False
        user_quiz_answer.answer_viewed = True
        user_quiz_answer.save(update_fields=['is_correct', 'answer_viewed'])
        serializer = self.get_serializer(instance, context={"request": request})
        return Response(serializer.data)


class FinishQuiz(PrivateSONRendererMixin, viewsets.GenericViewSet):
    queryset = (Quiz.objects.
                prefetch_related('user_quiz_reports').
                prefetch_related('user_quiz_questions').
                prefetch_related('questions').all())

    def finish_quiz(self, request, *args, **kwargs):
        instance = self.get_object()
        user = request.user
        user_quiz_report = instance.user_quiz_reports.filter(Q(user=user) & Q(finished=False)).first()
        if not user_quiz_report:
            raise YouCannotFinishQuiz
        user_quiz_answer = instance.user_quiz_questions.filter(
            Q(user=user) &
            Q(quiz_id=instance.id) &
            Q(report_id=user_quiz_report.id))

        questions_amount = instance.questions_amount
        correct_questions = user_quiz_answer.filter(is_correct=True).count()

        # for uqa in user_quiz_answer.filter(Q(is_correct__isnull=True)).all():
        #     uqa.is_correct = False
        #     uqa.user_answer = None
        #     uqa.save(update_fields=['is_correct', 'user_answer'])

        incorrect_questions = questions_amount - correct_questions
        data = {
            'correct_questions': correct_questions,
            'incorrect_questions': incorrect_questions,
            'used_hints': user_quiz_answer.filter(used_hints=True).count(),
            'viewed_answer': user_quiz_answer.filter(answer_viewed=True).count()
        }
        # user_quiz_report.finished = True
        # user_quiz_report.save(update_fields=['finished'])

        return Response(data)


class AssessmentView(PrivateSONRendererMixin, GenericViewSet):
    lookup_field = 'uuid'
    queryset = UserAssessment.objects.all()
    serializer_class = AssessmentSubjectsSerializer
    pagination_class = None

    def get_serializer_class(self):
        if self.action == "retrieve":
            return AssessmentSerializer
        elif self.action == 'create':
            return AssessmentCreateSerializer
        return AssessmentSubjectsSerializer

    def retrieve(self, request, *args, **kwargs):
        assessment = self.get_object()
        assessment.updated_at = timezone.now()
        assessment.save()
        serializer = self.get_serializer(assessment, many=False)
        return Response(serializer.data)

    def list(self, request, *args, **kwargs):
        subjects = Subject.objects.filter(enable_sor_soch=True)
        serializer = SubjectSerializer(subjects, many=True, context={'request': request,
                                                                     'assessment_view': True})
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AssessmentCheckAnswerView(PrivateSONRendererMixin, APIView):
    serializer_class = CheckAnswerSerializer

    def post(self, request, *args, **kwargs):
        user = request.user
        serializer = CheckAnswerSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer_data = serializer.validated_data
        assessment_uuid = kwargs.get('uuid')
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
        uqq = UserAssessmentResult.objects.filter(
            Q(user=user) & Q(question_id=question_id) & Q(assessment__uuid=assessment_uuid)).first()
        if uqq:
            uqq.answers.clear()
        is_correct = True
        correct_answer_count = 0
        for answer in answers:
            is_correct = True
            if answer.question.type == QuestionType.open_answer:
                uqq.user_answer = open_answer
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
                uqq.assessment.updated_at = timezone.now()
                uqq.assessment.save()
            data.append({
                'answer_id': answer.id,
                'user_answer': open_answer,
                'is_correct': is_correct,
                'life_count': 4,
                'show_report': False
            })
            if is_correct:
                correct_answer_count += 1
        if answers.count() == correct_answer_count:
            uqq.is_correct = is_correct
        else:
            uqq.is_correct = False
        uqq.save(update_fields=['is_correct', 'user_answer'])

        user_questions = UserAssessmentResult.objects.filter(user=user, assessment__uuid=assessment_uuid)
        if user_questions.count() == user_questions.filter(is_correct__isnull=False).count():
            for d in data:
                d['show_report'] = True
        return Response(data)


class FinishAssessmentView(PrivateSONRendererMixin, viewsets.GenericViewSet):
    queryset = (UserAssessment.objects.all())
    lookup_field = 'uuid'

    def finish_assessment(self, request, *args, **kwargs):
        user_assessment = self.get_object()
        user = request.user
        print(user.id)
        print(user_assessment.id)
        if user_assessment.user != user:
            raise YouCannotFinishQuiz
        if not user_assessment.end_datetime:
            user_assessment.end_datetime = timezone.now()
        user_quiz_answer = user_assessment.user_assessment_results.filter(user=user)
        print(user_quiz_answer.filter(is_correct=True).count())

        questions_amount = user_assessment.subject.sor_question_count
        correct_questions = user_quiz_answer.filter(is_correct=True).count()

        incorrect_questions = questions_amount - correct_questions
        duration = user_assessment.end_datetime - user_assessment.start_datetime
        duration_seconds = duration.total_seconds()
        data = {
            'correct_questions': correct_questions,
            'incorrect_questions': incorrect_questions,
            'duration': duration_seconds,
        }
        # user_assessment.is_finished = True
        # user_assessment.save(update_fields=['is_finished'])

        return Response(data)
