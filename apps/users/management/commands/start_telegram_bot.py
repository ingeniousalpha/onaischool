# Django команда для запуска бота
from django.core.management import BaseCommand

from apps.users.management.telegram_bot import main


class Command(BaseCommand):
    help = 'Запуск Telegram бота'

    def handle(self, *args, **kwargs):
        main()