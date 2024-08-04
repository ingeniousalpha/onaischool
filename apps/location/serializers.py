from rest_framework import serializers

from apps.common.serializers import AbstractNameSerializer
from apps.content.serializers import SchoolSerializer
from apps.location.models import City


class CitySerializer(AbstractNameSerializer):
    schools = serializers.SerializerMethodField()

    class Meta:
        model = City
        fields = ['id', 'name', 'schools']

    def get_schools(self, obj):
        return SchoolSerializer(obj.schools, many=True).data
