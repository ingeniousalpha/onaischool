from django.urls import path
from rest_framework.routers import DefaultRouter

from apps.analytics.views import TopicQuizzesView, CheckAnswerView, EntranceExamView, EntranceExamCheckAnswerView, \
    FinishEntranceExamView, QuizView, FinishQuiz, AssessmentView, AssessmentCheckAnswerView, FinishAssessmentView, \
    DiagnosticExamQuestionView, DiagnosticCheckAnswerView, DiagnosticExamView

urlpatterns = [
    path('exam-check-answer', EntranceExamCheckAnswerView.as_view()),
    path('finish-exam', FinishEntranceExamView.as_view()),
    path('check-answer', CheckAnswerView.as_view()),
    path('diagnostic-check-answer', DiagnosticCheckAnswerView.as_view()),
    path('assessment-check-answer/<uuid:uuid>', AssessmentCheckAnswerView.as_view()),
    path(
        'finish-assessment/<uuid:uuid>',
        FinishAssessmentView.as_view({'post': 'finish_assessment'}),
        name='finish-assessment'
    ),
    path(
        'finish-diagnostic-exam/<uuid:uuid>',
        DiagnosticExamView.as_view({'post': 'finish_diagnostic_exam'}),
        name='finish-diagnostic-exam'),
    path(
        'repeat-topics/<uuid:uuid>',
        DiagnosticExamView.as_view({'post': 'repeat_topics'}),
        name='repeat-topics'
    ),
    path(
        'show-hints/<int:pk>',
        QuizView.as_view({'get': 'show_hints'}),
        name='show-hints'
    ),
    path(
        'show-answer/<int:pk>',
        QuizView.as_view({'get': 'show_answer'}),
        name='view-answer'
    ),
    path(
        'finish-quiz/<int:pk>',
        FinishQuiz.as_view({'post': 'finish_quiz'}),
        name='finish-quiz'
    ),
]

router = DefaultRouter()
router.register('quiz', TopicQuizzesView, basename='topic-quizzes-view')
router.register('assessment', AssessmentView, basename='assessment-view')
router.register('entrance-exams', EntranceExamView, basename='entrance-exam-view')
router.register('diagnostic-exams', DiagnosticExamQuestionView, basename='diagnostic-exam-view')


urlpatterns += router.urls
