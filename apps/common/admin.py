from django.contrib import admin

from apps.common.models import HandledException

admin.site.site_header = "Onai school"
admin.site.site_title = "Onai school"
admin.site.index_title = ""


class HiddenAdmin(admin.ModelAdmin):
    def get_model_perms(self, request):
        return {}  # Hide model in admin list


class ChangeOnlyMixin:
    def has_add_permission(self, request, obj=None):
        return False


class ReadOnlyMixin(ChangeOnlyMixin):
    def has_change_permission(self, request, obj=None):
        return False


class ReadChangeOnlyMixin():
    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request, obj):
        return False


class ReadChangeOnlyTabularInline(ReadChangeOnlyMixin, admin.TabularInline):
    ...


class ReadChangeOnlyStackedInline(ReadChangeOnlyTabularInline, admin.StackedInline):
    ...


@admin.register(HandledException)
class HandledExceptionAdmin(admin.ModelAdmin):
    fields = (
        'id',
        'created_at',
        'code',
        'message',
        'stack_trace',
    )
    list_display = ('id', 'code', 'message', 'created_at')
    search_fields = ('id', 'code')
    readonly_fields = ('created_at', 'id')
    date_hierarchy = 'created_at'
