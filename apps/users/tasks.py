from django.db.models import Q
from requests.exceptions import ConnectionError, HTTPError, Timeout
import asyncio
from apps.users.models import User
from config import celery_app
from django.conf import settings
import telegram
import logging


@celery_app.task(
    autoretry_for=(ConnectionError, HTTPError, Timeout),
    default_retry_delay=2,
    retry_kwargs={"max_retries": 5},
    ignore_result=True,
)
def send_student_data():
    users = User.objects.filter(chat_id__isnull=False).all()
    text_parts = ['Доброе утро! ☀️\n']
    for user in users:
        for child in user.children.all():
            text_parts = [f'Имя/Фамилия: {child.full_name}\n']
            topic_names = []
            for q in child.user_quiz_questions.all():
                topic_name = q.quiz.topic.name.kk if q.quiz.topic.name.kk else q.quiz.topic.name.ru
                topic_names.append(topic_name)
            questions_count = child.user_quiz_questions.filter(
                Q(is_correct__isnull=False) |
                Q(answer_viewed=True) |
                Q(used_hints=True) |
                Q(answer_viewed=True)).count()
            correct_questions = child.user_quiz_questions.filter(is_correct=True).count()
            text_parts.append(f'Кол-во решенных задач: {questions_count}')
            text_parts.append(f'Кол-во правильно решенных задач: {correct_questions}')
            topics = ', '.join(topic_names)
            text_parts.append(f'Какие темы решал: {topics}')

        text = '\n'.join(text_parts)
        asyncio.run(async_send_telegram_message(chat_id=user.chat_id, text=text))


logger = logging.getLogger(__name__)


async def async_send_telegram_message(chat_id, text=None, file=None, html=False):
    if not chat_id:
        logger.error("Chat_id is empty")
        return False
    bot = telegram.Bot(token=settings.TELEGRAM_BOT_TOKEN)  # Get the bot token from settings
    try:
        if file:
            await bot.send_document(
                chat_id=chat_id,
                caption=text,
                document=file,
                parse_mode="HTML" if html else None,
                connect_timeout=30,
                read_timeout=30,
                write_timeout=30
            )
        elif text:
            await bot.send_message(
                chat_id=chat_id,
                text=text,
                parse_mode="HTML" if html else None,
                connect_timeout=30,
                read_timeout=30,
                write_timeout=30
            )
        else:
            logger.error("Text or file must not be empty")
            return False
        return True
    except Exception as e:
        logger.error(f"Failed to send message: {e}")
        return False