import os
from telegram import ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters  # Используем Filters
from django.conf import settings
from django.core.management.base import BaseCommand
from apps.users.models import User


def start(update, context):
    chat_id = update.message.chat_id
    button = KeyboardButton(text="Отправить номер телефона", request_contact=True)
    reply_markup = ReplyKeyboardMarkup([[button]], one_time_keyboard=True)
    context.bot.send_message(chat_id=chat_id, text="Привет! Отправь свой номер телефона для регистрации.",
                             reply_markup=reply_markup)


def handle_contact(update, context):
    contact = update.message.contact
    phone_number = contact.phone_number
    chat_id = update.message.chat_id
    print(f"Получен контакт: {phone_number}, chat_id: {chat_id}")
    user, created = User.objects.get_or_create(mobile_phone=phone_number)
    user.chat_id = chat_id
    user.save()

    context.bot.send_message(chat_id=chat_id, text="Спасибо! Ваш номер телефона сохранен.")


def send_message_to_user(phone_number, message_text, context):
    try:
        user = User.objects.get(phone_number=phone_number)
        chat_id = user.chat_id
        context.bot.send_message(chat_id=chat_id, text=message_text)
    except User.DoesNotExist:
        print(f"Пользователь с номером {phone_number} не найден.")


def handle_message(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Сообщение получено.")


def main():
    token = settings.TELEGRAM_BOT_TOKEN
    updater = Updater(token, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.contact, handle_contact))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
    updater.start_polling()
    updater.idle()


class Command(BaseCommand):
    help = 'Запуск Telegram бота'

    def handle(self, *args, **kwargs):
        main()
