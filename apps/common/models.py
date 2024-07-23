from uuid import uuid4

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _  # noqa
from django.contrib.contenttypes.fields import GenericRelation, GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from localized_fields.fields import LocalizedCharField, LocalizedTextField, LocalizedFileField

from .managers import MainManager
from .utils import OverwriteStorage


class MainModel(models.Model):
    objects = MainManager()

    class Meta:
        abstract = True


class CharIDModel(MainModel):
    id = models.CharField(
        _("Уникальный код"),
        max_length=16,
        primary_key=True
    )

    class Meta:
        abstract = True


class UUIDModel(MainModel):
    uuid = models.UUIDField(
        "Идентификатор",
        default=uuid4,
        unique=True,
        editable=False,
        db_index=True
    )

    class Meta:
        abstract = True


class TimestampModel(MainModel):
    created_at = models.DateTimeField("Время создания", default=timezone.now, db_index=True)
    updated_at = models.DateTimeField("Время последнего изменения", auto_now=True, db_index=True)

    class Meta:
        abstract = True

    @property
    def created_at_pretty(self):
        return self.created_at.strftime("%d/%m/%Y %H:%M:%S")  # noqa

    @property
    def updated_at_pretty(self):
        return self.updated_at.strftime("%d/%m/%Y %H:%M:%S")  # noqa


class MultipleModelFK(MainModel):
    content_type = models.ForeignKey(ContentType, on_delete=models.SET_NULL, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True)
    content_object = GenericForeignKey('content_type', 'object_id')


class HandledException(TimestampModel):
    code = models.TextField("Код ошибки", max_length=512)
    message = models.TextField("Описание ошибки", max_length=512)
    stack_trace = models.TextField("Traceback", null=True, blank=True)


class PriorityModel(MainModel):
    priority = models.PositiveIntegerField(
        db_index=True,
        default=0,
        verbose_name="Приоритет"
    )

    class Meta:
        abstract = True
        ordering = ('-priority',)


class AbstractNameModel(MainModel):
    name = LocalizedCharField(
        verbose_name=_("Название"),
        null=True,
        blank=True,
        required=True
    )

    class Meta:
        abstract = True

    def __str__(self):
        if self.name is not None:
            return str(self.name)
        return "Не задано"


class AbstractRequiredNameModel(MainModel):
    name = LocalizedCharField(
        verbose_name=_("Название"),
        null=True,
        required=True
    )

    class Meta:
        abstract = True

    def __str__(self):
        if self.name is not None:
            return str(self.name)
        return "Не задано"


class AbstractRequiredDescriptionModel(MainModel):
    description = LocalizedTextField(
        verbose_name=_("Описание"),
        null=True,
        required=True
    )

    class Meta:
        abstract = True

    def __str__(self):
        if self.description is not None:
            return str(self.description)
        return "Не задано"


class AbstractDescriptionModel(MainModel):
    description = LocalizedTextField(
        verbose_name=_("Описание"),
        null=True,
        blank=True
    )

    class Meta:
        abstract = True

    def __str__(self):
        if self.description is not None:
            return str(self.description)
        return "Не задано"
