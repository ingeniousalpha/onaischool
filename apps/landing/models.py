from django.db import models
from localized_fields.fields import LocalizedCharField, LocalizedTextField, LocalizedFileField
from apps.common.models import TimestampModel, AbstractDescriptionModel, AbstractTitleModel, PriorityModel
from django.utils.translation import gettext_lazy as _  # noqa


class Banner(TimestampModel, AbstractTitleModel, AbstractDescriptionModel, PriorityModel):
    image = models.ImageField('Backgroud image')


class CourseFeature(TimestampModel, AbstractTitleModel, PriorityModel):
    ...


class Course(TimestampModel, AbstractTitleModel, AbstractDescriptionModel, PriorityModel):
    features = models.ManyToManyField(CourseFeature, null=True, blank=True)

    class Meta:
        verbose_name = 'Курс'
        verbose_name_plural = 'Курсы'


class UserChampion(TimestampModel, AbstractDescriptionModel, PriorityModel):
    image = models.ImageField('Картинка')
    full_name = models.CharField(verbose_name="Имя/Фамилия", max_length=200)

    class Meta:
        verbose_name = 'Чемпион'
        verbose_name_plural = 'Чемпионы'


class UserReview(TimestampModel, PriorityModel):
    image = models.ImageField('Картинка', null=True, blank=True)

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'


class UserRequest(TimestampModel):
    REQUEST_TYPES = (
        ('question', 'Вопрос'),
        ('request', 'Заявка')
    )
    name = models.CharField(verbose_name="Имя", max_length=200)
    phone = models.CharField(verbose_name="Телефон", max_length=200)
    request_type = models.CharField(verbose_name="Тип запроса", max_length=100, choices=REQUEST_TYPES, default='question')
    comment = models.TextField(verbose_name="Комментарий", null=True, blank=True)
    text = models.TextField(verbose_name="Вопрос", null=True, blank=True)


class Teacher(AbstractDescriptionModel):
    image = models.ImageField()
    first_name = models.CharField(verbose_name="Имя", max_length=200)
    last_name = models.CharField(verbose_name="Фамилия", max_length=200)
    subject_name = LocalizedCharField(
        verbose_name=_("Название предмета"),
        null=True,
        required=['ru']
    )

    class Meta:
        verbose_name = 'Учитель'
        verbose_name_plural = 'Учители'
