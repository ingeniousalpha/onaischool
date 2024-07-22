from django.db.models import TextChoices


class Languages(TextChoices):
    KAZAKH = "kk", "Казахский"
    RUSSIAN = "ru", "Русский"
    ENGLISH = "en", "Английский"

