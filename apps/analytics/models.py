from django.db import models
from django.utils.translation import gettext_lazy as _
from localized_fields.fields import LocalizedTextField, LocalizedFileField

from apps import Grades
from apps.common.models import AbstractTitleModel
from apps.content import Quarter
from apps.content.models import Topic, Subject, Course, Direction, Chapter


class TestType(models.TextChoices):
    simulator = ('simulator', 'Тренажер')
    diagnostic = ('diagnostic', 'Диогностически')


class QuestionType(models.TextChoices):
    one_choice = ('one_choice', 'Выбрать один')
    open_answer = ('open_answer', 'Open answer')
    multiple_choice = ('multiple_choice', 'Выбрать несколько')


class AssessmentDays(models.TextChoices):
    first = ('1', '1')
    two = ('2', '2')
    three = ('3', '3')
    four = ('4', '4')


class Quiz(models.Model):
    subject = models.ForeignKey(Subject,
                                verbose_name="Предмет",
                                on_delete=models.SET_NULL,
                                null=True,
                                blank=True,
                                related_name='quizzes')

    course = models.ForeignKey(Course,
                               verbose_name="Курс",
                               on_delete=models.SET_NULL,
                               null=True,
                               blank=True,
                               related_name="quizzes")

    topic = models.ForeignKey(Topic,
                              verbose_name="Тема",
                              on_delete=models.SET_NULL,
                              null=True,
                              blank=True,
                              related_name='quizzes')

    type = models.CharField(max_length=255,
                            choices=TestType.choices,
                            default=TestType.simulator,
                            verbose_name='Тип теста')

    questions_amount = models.IntegerField(default=0)

    class Meta:
        verbose_name = _("Тест")
        verbose_name_plural = _("Тесты")

    def __str__(self):
        if self.topic:
            return f'{self.get_type_display()} {self.topic.name.ru}'
        return str(self.id)


class Question(AbstractTitleModel):

    image = LocalizedFileField(
        upload_to="images/analytics/",
        verbose_name="Картинка",
        null=True,
        blank=True,
    )
    explain_video = LocalizedTextField(
        verbose_name=_("Объяснительное видео"),
        null=True,
        blank=True
    )
    explanation_answer = LocalizedTextField(
        verbose_name=_("Объяснение ответа"),
        null=True,
        blank=True
    )
    explanation_answer_image = LocalizedFileField(
        upload_to="images/analytics/",
        verbose_name="Объяснение ответа(видео)",
        null=True,
        blank=True,
    )
    level = models.IntegerField(default=1)

    quiz = models.ForeignKey(
        Quiz,
        verbose_name="Тест",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='questions'
    )
    type = models.CharField(
        max_length=255,
        choices=QuestionType.choices,
        default=QuestionType.one_choice,
        verbose_name='Тип вопроса'
    )

    class Meta:
        verbose_name = _("Вопрос")
        verbose_name_plural = _("Вопросы")
        ordering = ['id']

    def __str__(self):
        return str(self.id)


class AbstractOption(models.Model):
    text = LocalizedTextField(
        verbose_name=_("Текст"),
        null=True,
        blank=True
    )
    image = LocalizedFileField(
        upload_to="images/analytics/",
        verbose_name="Картинка",
        null=True,
        blank=True,
    )
    is_correct = models.BooleanField(default=False)

    class Meta:
        abstract = True
        verbose_name = _("Вариант")
        verbose_name_plural = _("Варианты")


class AnswerOption(AbstractOption):
    question = models.ForeignKey(
        Question,
        verbose_name="Вопрос",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='answer_options'
    )


class EntranceExam(models.Model):
    direction = models.ForeignKey(
        Direction,
        verbose_name="Направление",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="entrance_exams"
    )
    duration = models.IntegerField(verbose_name="Длительность", default=0)

    class Meta:
        verbose_name = _("Вступительный тест")
        verbose_name_plural = _("Вступительные тесты")

    def __str__(self):
        if self.direction:
            return self.direction.name.ru
        return str(self.id)


class EntranceExamPerDay(AbstractTitleModel):
    passing_score = models.IntegerField(verbose_name="Проходной балл")
    duration = models.IntegerField(verbose_name="Длительность(в сек)", default=0)
    exam = models.ForeignKey(
        EntranceExam,
        verbose_name="Выступительный тест",
        on_delete=models.CASCADE,
        related_name='exam_per_day'
    )

    def __str__(self):
        if self.exam:
            return f'{self.exam.direction.name.ru} {self.title.ru}'
        return ''


class EntranceExamSubject(AbstractTitleModel):
    max_score = models.IntegerField(verbose_name="Максимальное количество баллов")
    questions_amount = models.IntegerField(verbose_name="Количество вопросов")
    exam_per_day = models.ForeignKey(
        EntranceExamPerDay,
        verbose_name="День",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='exam_subjects'
    )

    class Meta:
        verbose_name = _("Вступительный тест по предметом")
        verbose_name_plural = _("Вступительные тесты по предметом")


class ExamQuestion(AbstractTitleModel):

    image = LocalizedFileField(
        upload_to="images/analytics/",
        verbose_name="Картинка",
        null=True,
        blank=True,
    )
    assessment_subject = models.ForeignKey(
        EntranceExamSubject,
        verbose_name="Вступительный тест по предметом",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='exam_questions'
    )
    score = models.IntegerField(default=1)

    class Meta:
        verbose_name = _("Вопрос (Вступительный тест)")
        verbose_name_plural = _("Вопросы (Вступительный тест)")
        ordering = ['score']


class ExamAnswerOption(AbstractOption):
    exam_question = models.ForeignKey(
        ExamQuestion,
        verbose_name="Вопрос",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='exam_answer_options'
    )


class DiagnosticExam(AbstractTitleModel):

    enabled = models.BooleanField(verbose_name="Разрешен", default=True)
    questions_amount = models.IntegerField(default=1, verbose_name="Количество вопросов")
    duration = models.IntegerField("Длительность(минут)", default=1)

    class Meta:
        verbose_name = _("Диагностический тест")
        verbose_name_plural = _("Диагностический тесты")


class DiagnosticExamQuestion(AbstractTitleModel):
    topic = models.ForeignKey(
        Topic,
        verbose_name="Тема",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='diagnostic_exams'
    )
    grade = models.CharField(
        max_length=3,
        choices=Grades.choices,
        default=Grades.FIRST,
        verbose_name="Класс"
    )
    image = LocalizedFileField(
        upload_to="images/analytics/",
        verbose_name="Картинка",
        null=True,
        blank=True,
    )
    type = models.CharField(
        max_length=255,
        choices=QuestionType.choices,
        default=QuestionType.one_choice,
        verbose_name='Тип вопроса'
    )
    score = models.IntegerField(default=1)
    diagnostic_exam = models.ForeignKey(
        DiagnosticExam,
        verbose_name="Диагностический тест",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='diagnostic_exam_questions'
    )

    class Meta:
        verbose_name = _("Вопрос (Диагностический тест)")
        verbose_name_plural = _("Вопросы (Диагностический тест)")
        ordering = ['score']


class DiagnosticExamAnswerOption(AbstractOption):
    diagnostic_exam_question = models.ForeignKey(
        DiagnosticExamQuestion,
        verbose_name="Вопрос",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='diagnostic_exam_answer_options'
    )

