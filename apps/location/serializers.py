from rest_framework import serializers

from apps.common.serializers import AbstractNameSerializer
from apps.content.serializers import SchoolSerializer
from apps.location.models import City


class CitySerializer(AbstractNameSerializer):

    class Meta:
        model = City
        fields = ['id', 'name']


class CityDetailSerializer(CitySerializer):
    schools = serializers.SerializerMethodField()

    class Meta(CitySerializer.Meta):
        fields = CitySerializer.Meta.fields + ['schools']

    def get_schools(self, obj):
        return SchoolSerializer(obj.schools, many=True).data
