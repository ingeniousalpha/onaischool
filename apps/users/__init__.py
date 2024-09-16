from django.db.models import TextChoices

default_app_config = 'apps.users.apps.UsersConfig'


class GenderChoices(TextChoices):
    MALE = ("male", "Мужской")
    FEMALE = ("female", "Женский")