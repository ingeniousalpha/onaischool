from django.urls import path
from rest_framework.routers import DefaultRouter

from apps.analytics.views import TopicQuizzesView, CheckAnswerView, EntranceExamView, ExamQuestionView


urlpatterns = [
    path('check-answer', CheckAnswerView.as_view()),
    # path('exams/subjects/<pk:int>', ExamQuestionView.as_view())
]

router = DefaultRouter()
router.register('quiz', TopicQuizzesView, basename='topic-quizzes-view')
router.register('entrance-exams', EntranceExamView, basename='entrance-exam-view')


urlpatterns += router.urls
