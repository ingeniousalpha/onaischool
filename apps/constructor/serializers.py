from rest_framework import serializers

from apps.analytics.models import EntranceExam, DiagnosticExam
from apps.analytics.serializers import ExamPerDayForMainPageSerializer
from apps.common.mixins import UserPropertyMixin
from apps.content.serializers import TopicSerializerWithSubject


class MainPageSerializer(serializers.Serializer, UserPropertyMixin):
    current_topic = serializers.SerializerMethodField()
    current_exam = serializers.SerializerMethodField()
    diagnostic_exam = serializers.SerializerMethodField()

    class Meta:
        fields = ['current_topic', 'current_exam', 'diagnostic_exam']

    def get_diagnostic_exam(self, obj):

        user = self.user
        is_active = False
        exam_id = None
        for d in DiagnosticExam.objects.filter(enabled=True).all():
            if not user.user_diagnostic_reports.filter(diagnostic_exam_id=d.id).exists():
                exam_id = d.id
                is_active = True
                break
            elif user.user_diagnostic_reports.filter(diagnostic_exam_id=d.id, is_finished=False).exists():
                exam_id = d.id
                is_active = True
                break
        return {'is_active': is_active,
                'diagnostic_exam_id': exam_id}

    def get_current_topic(self, obj):
        return TopicSerializerWithSubject(obj.current_topic, context=self.context).data

    def get_current_exam(self, obj):
        if obj.current_exam_per_day:
            return ExamPerDayForMainPageSerializer(obj.current_exam_per_day, context=self.context).data
        else:
            entrance_exam = EntranceExam.objects.first()
            return ExamPerDayForMainPageSerializer(entrance_exam.exam_per_day.first(), context=self.context).data