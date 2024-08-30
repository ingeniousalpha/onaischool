from django.urls import path
from rest_framework.routers import DefaultRouter

from apps.analytics.views import TopicQuizzesView, CheckAnswerView, EntranceExamView, EntranceExamCheckAnswerView, \
    FinishEntranceExamView


urlpatterns = [
    path('check-answer', CheckAnswerView.as_view()),
    path('exam-check-answer', EntranceExamCheckAnswerView.as_view()),
    path('finish-exam', FinishEntranceExamView.as_view())
]

router = DefaultRouter()
router.register('quiz', TopicQuizzesView, basename='topic-quizzes-view')
router.register('entrance-exams', EntranceExamView, basename='entrance-exam-view')


urlpatterns += router.urls
