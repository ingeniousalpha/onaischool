from django.db import models
from django.utils.translation import gettext_lazy as _
from localized_fields.fields import LocalizedTextField, LocalizedFileField

from apps.common.models import PriorityModel, AbstractRequiredNameModel, AbstractRequiredDescriptionModel, \
    AbstractDescriptionModel
from apps.content import Grades, Quarter
from apps.location.models import City


class School(PriorityModel, AbstractRequiredNameModel):
    city = models.ForeignKey(City, verbose_name="Город",
                             on_delete=models.SET_NULL, null=True, blank=True, related_name="schools")

    class Meta:
        verbose_name = _("Школа")
        verbose_name_plural = _("Школы")
        ordering = ['priority']


class Direction(PriorityModel, AbstractRequiredNameModel, AbstractRequiredDescriptionModel):
    image = LocalizedFileField(
        upload_to="images/",
        verbose_name="Картинка",
        null=True,
        blank=True,
    )
    enable_all = models.BooleanField(default=False)

    class Meta:
        verbose_name = _("Direction")
        verbose_name_plural = _("Directions")
        ordering = ['priority']

    def __str__(self):
        return self.name.ru


class Subject(PriorityModel, AbstractRequiredNameModel):
    direction = models.ForeignKey(Direction, verbose_name="Направление",
                                  on_delete=models.SET_NULL, null=True, blank=True, related_name="subjects")
    enable_sor_soch = models.BooleanField(default=False, verbose_name="Сор/Соч разрешен")
    sor_question_count = models.IntegerField(default=0, verbose_name="СОР(Суммативное Оценивание за Раздел) кол-во")
    soch_question_count = models.IntegerField(default=0, verbose_name="СОЧ(Суммативное Оценивание за Четверть) кол-во")
    sor_duration = models.IntegerField("СОР(Суммативное Оценивание за Раздел) длительность(минут)", default=1)
    soch_duration = models.IntegerField("СОЧ(Суммативное Оценивание за Четверть) длительность(минут)", default=1)

    class Meta:
        verbose_name = _("Предмет")
        verbose_name_plural = _("Предметы")
        ordering = ['priority']

    def __str__(self):
        if self.direction:
            return f'{self.direction.name.ru} {self.name.ru}'
        return f"Subject {self.name.ru}"


class Course(PriorityModel, AbstractRequiredNameModel):
    grade = models.CharField(max_length=3, choices=Grades.choices, default=Grades.FIRST, verbose_name="Класс")
    subject = models.ForeignKey(Subject, verbose_name="Предмет",
                                on_delete=models.SET_NULL, null=True, blank=True, related_name='courses')

    class Meta:
        verbose_name = _("Курс")
        verbose_name_plural = _("Курсы")
        ordering = ['grade', 'priority']

    def __str__(self):
        return f"{self.subject} {self.grade}кл "


class Chapter(PriorityModel, AbstractRequiredNameModel):
    quarter = models.CharField(max_length=10, choices=Quarter.choices, default=Quarter.FIRST, verbose_name="Четверть")
    course = models.ForeignKey(Course, verbose_name="Курс",
                               on_delete=models.SET_NULL, null=True, blank=True, related_name="chapters")

    class Meta:
        verbose_name = _("Раздел")
        verbose_name_plural = _("Разделы")
        ordering = ['quarter', 'priority']

    def __str__(self):
        return f"{self.name.ru} {self.quarter} четверть {self.course}"


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
                                on_delete=models.CASCADE, related_name="topics")

    class Meta:
        verbose_name = _("Тема")
        verbose_name_plural = _("Темы")
        ordering = ['priority']
