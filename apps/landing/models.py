from django.db import models

from apps.common.models import TimestampModel, AbstractDescriptionModel


class UserRequest(TimestampModel):
    name = models.CharField(verbose_name="Имя", max_length=200)
    phone = models.CharField(verbose_name="Телефон", max_length=200)
    comment = models.TextField(verbose_name="Комментарий", null=True, blank=True)


class UserQuestion(TimestampModel):
    name = models.CharField(verbose_name="Имя", max_length=200)
    phone = models.CharField(verbose_name="Телефон", max_length=200)
    text = models.TextField(verbose_name="Вопрос")


class Teacher(AbstractDescriptionModel):
    image = models.ImageField()
    first_name = models.CharField(verbose_name="Имя", max_length=200)
    last_name = models.CharField(verbose_name="Фамилия", max_length=200)
