from rest_framework.viewsets import ReadOnlyModelViewSet

from apps.common.mixins import PublicJSONRendererMixin
from apps.location.models import City
from apps.location.serializers import CitySerializer


class CitiesView(PublicJSONRendererMixin, ReadOnlyModelViewSet):
    queryset = City.objects.all()
    serializer_class = CitySerializer

    def get_serializer_class(self):
        if self.action == "retrieve":
            return CitySerializer
        return CitySerializer

