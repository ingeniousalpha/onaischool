from django.db import models
from django.utils.translation import gettext_lazy as _
from localized_fields.fields import LocalizedTextField, LocalizedFileField

from apps.common.models import PriorityModel, AbstractRequiredNameModel, AbstractRequiredDescriptionModel, \
    AbstractDescriptionModel
from apps.content import Grades, Quarter


class School(PriorityModel, AbstractRequiredNameModel):
    ...

    class Meta:
        verbose_name = _("Школа")
        verbose_name_plural = _("Школы")


class Direction(PriorityModel, AbstractRequiredNameModel, AbstractRequiredDescriptionModel):
    image = LocalizedFileField(
        upload_to="images/",
        verbose_name="Картинка",
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = _("Direction")
        verbose_name_plural = _("Directions")


class Subject(PriorityModel, AbstractRequiredNameModel):
    direction = models.ForeignKey(Direction, verbose_name="Направление",
                                  on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        verbose_name = _("Предмет")
        verbose_name_plural = _("Предметы")


class Course(PriorityModel, AbstractRequiredNameModel):
    grade = models.CharField(max_length=3, choices=Grades.choices, default=Grades.FIRST, verbose_name="Класс")
    subject = models.ForeignKey(Subject, verbose_name="Предмет",
                                on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        verbose_name = _("Курс")
        verbose_name_plural = _("Курсы")


class Chapter(PriorityModel, AbstractRequiredNameModel):
    quarter = models.CharField(max_length=10, choices=Quarter.choices, default=Quarter.FIRST, verbose_name="Четверть")
    course = models.ForeignKey(Course, verbose_name="Курс",
                               on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        verbose_name = _("Раздел")
        verbose_name_plural = _("Разделы")


class Topic(PriorityModel, AbstractRequiredNameModel, AbstractDescriptionModel):
    video_link = LocalizedTextField(
        verbose_name=_("Ссылка на видео"),
        null=True,
        blank=True
    )
    image = LocalizedFileField(
        upload_to="images/",
        verbose_name="Картинка",
        null=True,
        blank=True,
    )
    chapter = models.ForeignKey(Chapter, verbose_name="Раздел",
                                on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        verbose_name = _("Тема")
        verbose_name_plural = _("Темы")