import uuid as uuid_lib
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from phonenumber_field.modelfields import PhoneNumberField

from config.settings import Languages
from . import GenderChoices
from .managers import UserManager

from .. import Grades, Roles
from ..analytics.models import Question, AnswerOption, Quiz, EntranceExam, ExamQuestion, ExamAnswerOption, \
    EntranceExamPerDay, DiagnosticExam, DiagnosticExamQuestion, DiagnosticExamAnswerOption
from ..common.models import TimestampModel
from ..content import Quarter
from ..content.models import School, Course, Topic


class User(PermissionsMixin, AbstractBaseUser):
    class Meta:
        verbose_name = _("Учетная запись")
        verbose_name_plural = _("Учетная запись")

    uuid = models.UUIDField("UUID пользователя", default=uuid_lib.uuid4, unique=True)
    email = models.EmailField("Почта", max_length=40, unique=True, null=True, blank=True)
    full_name = models.CharField("Имя", max_length=256, null=True, blank=True)
    mobile_phone = PhoneNumberField("Моб. телефон", blank=True, null=True)
    secret_key = models.UUIDField("Секретный ключ", default=uuid_lib.uuid4, unique=True)
    language = models.CharField(max_length=20, choices=Languages.choices, default=Languages.KAZAKH, verbose_name="Язык")
    chat_id = models.CharField(max_length=50, null=True, blank=True)
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children',
        verbose_name=_("Родитель")
    )
    school = models.ForeignKey(
        School,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='students',
        verbose_name=_("Школа")
    )
    enabled_courses = models.ManyToManyField(
        Course,
        blank=True,
        related_name="enrolled_users",
        verbose_name="Users"
    )
    enabled_topics = models.ManyToManyField(
        Topic,
        blank=True,
        related_name="enrolled_users",
        verbose_name="Users"
    )
    grade = models.CharField(max_length=3, choices=Grades.choices, default=Grades.FIRST, verbose_name="Класс")
    role = models.CharField(max_length=50, choices=Roles.choices, default=Roles.STUDENT)
    is_active = models.BooleanField("Активный", default=True)
    is_staff = models.BooleanField("Сотрудник", default=False)
    is_email_confirmed = models.BooleanField("Почта подтверждена", default=False)
    is_mobile_phone_verified = models.BooleanField(default=False)
    avatar_image = models.ImageField(null=True, blank=True)
    created_at = models.DateTimeField(_("Создан"), default=timezone.now)
    updated_at = models.DateTimeField(_("Обновлен"), auto_now=True)
    current_topic = models.ForeignKey(
        Topic,
        on_delete=models.CASCADE,
        related_name="users",
        null=True,
        blank=True
    )
    current_exam_per_day = models.ForeignKey(
        EntranceExamPerDay,
        on_delete=models.CASCADE,
        related_name="users",
        null=True,
        blank=True
    )
    avatar = models.ForeignKey(
        "Avatar",
        on_delete=models.CASCADE,
        related_name="users",
        null=True,
        blank=True
    )

    USERNAME_FIELD = "email"
    objects = UserManager()

    def __str__(self):
        return f"{self.full_name} {self.mobile_phone}"

    # @property
    # def username(self):
    #     if self.mobile_phone:
    #         return str(self.mobile_phone)
    #     return self.email

    def has_perm(self, perm, obj=None):
        if not self.is_active:
            return False
        if self.is_superuser:
            return True
        return perm in self.get_all_permissions(obj)

    def has_module_perms(self, app_label):
        if self.is_superuser:
            return True
        return self.is_active and any(
            perm[: perm.index(".")] == app_label for perm in self.get_all_permissions()
        )

    # def get_username(self):
    #     return self.mobile_phone

    def set_password(self, raw_password):
        super(User, self).set_password(raw_password)

    def set_active(self):
        self.is_active = True
        self.is_email_confirmed = True
        self.save(update_fields=['is_active', 'is_email_confirmed'])

    def get_is_active(self):
        if self.created_at + timezone.timedelta(days=1) > timezone.now():
            return True
        return self.is_active


class Avatar(models.Model):
    gender = models.CharField(max_length=20, choices=GenderChoices.choices, default=GenderChoices.MALE, verbose_name="Язык")
    image = models.ImageField(verbose_name="Смайлик", null=False, upload_to="images/users/")

    class Meta:
        verbose_name = _("Аватарка")
        verbose_name_plural = _("Аватары")
        ordering = ('gender',)


class MyTopic(TimestampModel):
    user = models.ForeignKey(
        User,
        verbose_name="Пользователь",
        on_delete=models.CASCADE,
        null=True, blank=True, related_name="my_topics")

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="my_topic")
    topic = models.ForeignKey(
        Topic,
        on_delete=models.CASCADE,
        related_name="my_topics"
    )
    is_completed = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']


class UserQuizReport(TimestampModel):
    quiz = models.ForeignKey(
        Quiz,
        on_delete=models.CASCADE,
        null=False,
        related_name='user_quiz_reports'
    )
    user = models.ForeignKey(
        User,
        verbose_name="Пользователь",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="user_quiz_reports"
    )
    finished = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']


class UserQuizQuestion(TimestampModel):
    quiz = models.ForeignKey(
        Quiz,
        on_delete=models.CASCADE,
        null=False,
        related_name='user_quiz_questions'
    )
    user = models.ForeignKey(
        User,
        verbose_name="Пользователь",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="user_quiz_questions")
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        null=False,
        related_name='user_quiz_questions'
    )
    report = models.ForeignKey(
        UserQuizReport,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='user_quiz_questions'
    )
    answers = models.ManyToManyField(
        AnswerOption,
        blank=True,
        related_name='user_quiz_questions'
    )
    user_answer = models.CharField(max_length=100, null=True, blank=True)
    answer_viewed = models.BooleanField(default=False)
    used_hints = models.BooleanField(default=False)
    is_correct = models.BooleanField(null=True, blank=True)

    class Meta:
        ordering = ['id']


class UserExamQuestion(TimestampModel):
    entrance_exam = models.ForeignKey(
        EntranceExam,
        on_delete=models.CASCADE,
        related_name='user_exam_questions',
        null=True,
        blank=True
    )
    exam_question = models.ForeignKey(
        ExamQuestion,
        on_delete=models.CASCADE,
        null=False,
        related_name='user_exam_questions'
    )
    exam_result = models.ForeignKey(
        "UserExamResult",
        on_delete=models.CASCADE,
        null=True,
        related_name='user_exam_questions'
    )
    user = models.ForeignKey(
        User,
        verbose_name="Пользователь",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="user_exam_questions")
    answers = models.ManyToManyField(
        ExamAnswerOption,
        blank=True,
        related_name='user_exam_questions'
    )
    user_answer = models.CharField(max_length=255, null=True, blank=True)
    is_correct = models.BooleanField(null=True, blank=True)

    class Meta:
        ordering = ['id']


class UserExamResult(TimestampModel):
    uuid = models.UUIDField(default=uuid_lib.uuid4, editable=False, null=True, unique=True)
    entrance_exam = models.ForeignKey(
        EntranceExam,
        verbose_name="Выступительный тест",
        on_delete=models.CASCADE,
        related_name="user_exam_results",
    )
    exam_per_day = models.ForeignKey(
        EntranceExamPerDay,
        verbose_name="Выступительный тест по дням",
        on_delete=models.CASCADE,
        null=True, blank=True,
        related_name="user_exam_results",
    )
    user = models.ForeignKey(
        User,
        verbose_name="Пользователь",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="user_exam_results")
    start_datetime = models.DateTimeField(_("Время начала"), auto_now_add=True, db_index=True)
    end_datetime = models.DateTimeField(null=True, blank=True, verbose_name='Время окончания')
    correct_score = models.IntegerField(default=0)

    class Meta:
        ordering = ['-created_at']


class UserAssessment(models.Model):
    ASSESSMENT_TYPE_CHOICES = [
        ('SOR', 'Суммативное Оценивание за Раздел (СОР)'),
        ('SOCH', 'Суммативное Оценивание за Четверть (СОЧ)')
    ]
    uuid = models.UUIDField(default=uuid_lib.uuid4, editable=False, unique=True)
    subject = models.ForeignKey("content.Subject", on_delete=models.CASCADE, related_name='assessments', verbose_name='Предмет')
    quarter = models.CharField(max_length=10, choices=Quarter.choices, null=True, blank=True, verbose_name="Четверть")
    chapter = models.ForeignKey("content.Chapter", on_delete=models.CASCADE, null=True, blank=True, related_name='assessments', verbose_name='Раздел')
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="user_assessments")
    user = models.ForeignKey(
        User,
        verbose_name="Пользователь",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="user_assessments")
    assessment_type = models.CharField(max_length=4, choices=ASSESSMENT_TYPE_CHOICES, verbose_name='Тип оценивания')
    level = models.IntegerField(default=1)
    questions = models.ManyToManyField(Question)
    start_datetime = models.DateTimeField(_("Время начала"), auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(_("Время последнего изменения"), auto_now=True, db_index=True)
    end_datetime = models.DateTimeField(null=True, blank=True, verbose_name='Время окончания')
    is_finished = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.assessment_type} {self.subject.name.ru}"


class UserAssessmentResult(TimestampModel):
    user = models.ForeignKey(
        User,
        verbose_name="Пользователь",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="user_assessment_results")
    assessment = models.ForeignKey(
        UserAssessment,
        verbose_name="Сор/Соч",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="user_assessment_results")
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        null=False,
        related_name='user_assessment_results'
    )
    answers = models.ManyToManyField(
        AnswerOption,
        blank=True,
        related_name='user_assessment_results'
    )
    user_answer = models.CharField(max_length=100, null=True, blank=True)
    is_correct = models.BooleanField(null=True, blank=True)


class UserDiagnosticExamReport(models.Model):
    uuid = models.UUIDField(default=uuid_lib.uuid4, editable=False, unique=True)
    user = models.ForeignKey(
        User,
        verbose_name="Пользователь",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="user_diagnostic_reports"
    )
    diagnostic_exam = models.ForeignKey(
        DiagnosticExam,
        verbose_name="Диагностический тест",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="user_diagnostic_reports"
    )
    questions = models.ManyToManyField(
        DiagnosticExamQuestion,
        blank=True,
        related_name='user_diagnostic_reports'
    )
    is_finished = models.BooleanField(default=False)


class UserDiagnosticsResult(TimestampModel):
    user = models.ForeignKey(
        User,
        verbose_name="Пользователь",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="user_diagnostic_results")
    user_diagnostic_report = models.ForeignKey(
        UserDiagnosticExamReport,
        verbose_name="Репорт",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="user_diagnostic_results")
    question = models.ForeignKey(
        DiagnosticExamQuestion,
        on_delete=models.CASCADE,
        null=False,
        related_name='user_diagnostic_results'
    )
    answers = models.ManyToManyField(
        DiagnosticExamAnswerOption,
        blank=True,
        related_name='user_diagnostic_results'
    )
    user_answer = models.CharField(max_length=100, null=True, blank=True)
    is_correct = models.BooleanField(null=True, blank=True)
