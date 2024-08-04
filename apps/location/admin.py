from django.contrib import admin
from localized_fields.admin import LocalizedFieldsAdminMixin

from apps.location.models import City


@admin.register(City)
class CityAdmin(LocalizedFieldsAdminMixin, admin.ModelAdmin):
    list_display = ('id', 'name', 'priority')
