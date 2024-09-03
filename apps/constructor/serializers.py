from rest_framework import serializers

from apps.analytics.models import EntranceExam
from apps.analytics.serializers import ExamPerDayForMainPageSerializer
from apps.content.serializers import TopicSerializerWithSubject


class MainPageSerializer(serializers.Serializer):
    current_topic = serializers.SerializerMethodField()
    current_exam = serializers.SerializerMethodField()

    class Meta:
        fields = ['current_topic', 'current_exam']

    def get_current_topic(self, obj):
        return TopicSerializerWithSubject(obj.current_topic, context=self.context).data

    def get_current_exam(self, obj):
        if obj.current_exam_per_day:
            return ExamPerDayForMainPageSerializer(obj.current_exam_per_day, context=self.context).data
        else:
            entrance_exam = EntranceExam.objects.first()
            return ExamPerDayForMainPageSerializer(entrance_exam.exam_per_day.first(), context=self.context).data