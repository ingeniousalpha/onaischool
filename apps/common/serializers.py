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


class AbstractNameSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()

    class Meta:
        abstract = True

    def get_name(self, obj):
        return obj.name.translate()


class AbstractDescriptionSerializer(serializers.ModelSerializer):
    description = serializers.SerializerMethodField()

    class Meta:
        abstract = True

    def get_description(self, obj):
        return obj.description.translate()


class AbstractImageSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        abstract = True

    def get_image(self, obj):
        request = self.context.get('request')
        if obj.image:
            return request.build_absolute_uri(obj.image.translate().url)
        return ''

