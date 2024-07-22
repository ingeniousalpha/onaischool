from rest_framework import serializers


class RequestPropertyMixin:
    @property
    def request(self):
        return self.context.get('request')


class RequestUserPropertyMixin(RequestPropertyMixin):
    @property
    def user(self):
        if self.request and self.request.user.is_authenticated:
            return self.request.user


class FilePathMethodMixin:

    def file_path(self, file_field):
        return self.context.get('request').build_absolute_uri(file_field.url)
