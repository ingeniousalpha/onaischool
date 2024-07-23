from django.db.models import TextChoices
from django.utils.translation import gettext_lazy as _


class Grades(TextChoices):
    FIRST = '1', _('Grade 1')
    SECOND = '2', _('Grade 2')
    THIRD = '3', _('Grade 3')
    FOURTH = '4', _('Grade 4')
    FIFTH = '5', _('Grade 5')
    SIXTH = '6', _('Grade 6')
    SEVENTH = '7', _('Grade 7')
    EIGHTH = '8', _('Grade 8')
    NINTH = '9', _('Grade 9')
    TENTH = '10', _('Grade 10')
    ELEVENTH = '11', _('Grade 11')
    TWELFTH = '12', _('Grade 12')


class Quarter(TextChoices):
    FIRST = '1', _('Grade 1')
    SECOND = '2', _('Grade 2')
    THIRD = '3', _('Grade 3')
    FOURTH = '4', _('Grade 4')
