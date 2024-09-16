from rest_framework.viewsets import ReadOnlyModelViewSet

from apps.common.mixins import PublicJSONRendererMixin
from apps.location.models import City
from apps.location.serializers import CityDetailSerializer


class CitiesView(PublicJSONRendererMixin, ReadOnlyModelViewSet):
    queryset = City.objects.all()
    serializer_class = CityDetailSerializer
    pagination_class = None

    def get_serializer_class(self):
        if self.action == "retrieve":
            return CityDetailSerializer
        return CityDetailSerializer

