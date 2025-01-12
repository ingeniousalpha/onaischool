import asyncio
import logging
import os
import pickle
import sys
from base64 import b64decode
from typing import Union

from aiogram import Dispatcher, Bot, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode, ContentType
from aiogram.filters import CommandStart
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, Message, ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from sqlalchemy import create_engine, sql, Connection
from sqlalchemy.orm import Session


TOKEN = os.getenv("DIAGNOSTIC_BOT_TOKEN")
DB_HOST = os.getenv("DB_HOST", "onai-db")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "onaidb")
DB_USER = os.getenv("DB_USER", "onaidb")
DB_PASSWORD = os.getenv("DB_PASSWORD", "onaidb")


def get_engine(application_name: str):
    return create_engine("postgresql+psycopg2://{user}:{password}@{host}:{port}/{dbname}".format(
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        pool_recycle=60 * 30,
    ), connect_args={"application_name": application_name})


engine = get_engine(__name__)
dp = Dispatcher()


def get_constance_value(connection: Union[Connection, Session], key: str, default=None):
    b64_value = connection.execute(
        sql.text('select value from constance_config where key = :key'), {'key': key}
    ).scalar()
    if b64_value is None:
        return default
    value = pickle.loads(b64decode(b64_value))
    return value


@dp.message(CommandStart())
async def command_start_handler(message: Message):
    if message.from_user.is_bot:
        return None
    with Session(engine) as session:
        exam_id = get_constance_value(session, 'BOT_EXAM_ID')
        unavailable_text = get_constance_value(session, 'BOT_UNAVAILABLE_TEXT')
        is_valid = False
        if exam_id:
            exam_data = await get_exam_questions()
            if exam_data:
                is_valid = True
        if is_valid:
            await message.answer(
                text=get_constance_value(session, 'BOT_INITIAL_TEXT'),
                reply_markup=build_language_buttons()
            )
        else:
            await message.answer(text=unavailable_text)


async def get_exam_questions():
    exam_data = []
    with Session(engine) as session:
        exam_id = get_constance_value(session, 'BOT_EXAM_ID')
        if not exam_id:
            return None
        exam_questions = session.execute(sql.text(f"""
            SELECT id, title -> 'ru' as text_ru, title -> 'kk' as text_kk
            FROM analytics_diagnosticexamquestion
            WHERE type = 'one_choice' AND diagnostic_exam_id = {exam_id} ORDER BY id ASC
        """)).fetchall()
        for exam_question in exam_questions:
            exam_question_data = {
                "id": exam_question[0],
                "text_ru": exam_question[1].replace('<', '&lt;'),
                "text_kk": exam_question[2].replace('<', '&lt;'),
                "answers": []
            }
            question_answers = session.execute(sql.text(f"""
                SELECT id, text -> 'ru' as text_ru, text -> 'kk' as text_kk, is_correct
                FROM analytics_diagnosticexamansweroption
                WHERE diagnostic_exam_question_id = {exam_question[0]}
                ORDER BY id ASC
            """)).fetchall()
            for question_answer in question_answers:
                exam_question_data["answers"].append(
                    {
                        "id": question_answer[0],
                        "text_ru": question_answer[1].replace('<', '&lt;'),
                        "text_kk": question_answer[2].replace('<', '&lt;'),
                        "is_correct": question_answer[3]
                    }
                )
            exam_data.append(exam_question_data)
    global questions, question_count
    questions = exam_data
    question_count = len(exam_data)
    return exam_data


def build_language_buttons():
    with Session(engine) as session:
        button_rows = [
            [
                InlineKeyboardButton(
                    text=get_constance_value(session, 'BOT_INITIAL_BUTTON_TEXT_KK'),
                    callback_data="set_language_kk"
                ),
                InlineKeyboardButton(
                    text=get_constance_value(session, 'BOT_INITIAL_BUTTON_TEXT_RU'),
                    callback_data="set_language_ru"
                )
            ]
        ]
    return InlineKeyboardMarkup(inline_keyboard=button_rows)


@dp.callback_query(F.data.startswith('set_language_'))
async def callback_language_handler(callback_query: CallbackQuery):
    language = callback_query.data.replace('set_language_', '')
    with Session(engine) as session:
        welcome_text = get_constance_value(session, f'BOT_WELCOME_TEXT_{language.upper()}')
        user_session = session.execute(sql.text(f"""
            SELECT * FROM analytics_diagnosticbotsession
            WHERE message_id = {callback_query.message.message_id}
            ORDER BY id DESC
        """)).fetchone()
        if user_session:
            session.execute(sql.text(f"""
                UPDATE analytics_diagnosticbotsession
                SET language = '{language}'
                WHERE user_id = {callback_query.from_user.id}
            """))
        else:
            session.execute(sql.text(f"""
                INSERT INTO analytics_diagnosticbotsession (user_id, message_id, language, phone_number)
                VALUES ({callback_query.from_user.id}, {callback_query.message.message_id}, '{language}', NULL)
            """))
        session.commit()
    await callback_query.message.edit_text(text=welcome_text, reply_markup=build_initial_buttons(language))


def build_initial_buttons(language):
    with Session(engine) as session:
        welcome_button_text = get_constance_value(session, f'BOT_WELCOME_BUTTON_TEXT_{language.upper()}')
    button_rows = [[InlineKeyboardButton(text=welcome_button_text, callback_data="get_question_0")]]
    return InlineKeyboardMarkup(inline_keyboard=button_rows)


@dp.callback_query(F.data.startswith('get_question_'))
async def callback_question_handler(callback_query: CallbackQuery):
    question_index = int(callback_query.data.replace('get_question_', ''))
    question = questions[question_index]
    with Session(engine) as session:
        user_session = session.execute(sql.text(f"""
            SELECT id, language
            FROM analytics_diagnosticbotsession
            WHERE message_id = {callback_query.message.message_id}
        """)).fetchone()
        user_answer = session.execute(sql.text(f"""
            SELECT answer_id
            FROM analytics_diagnosticbotuseranswer
            WHERE session_id = {user_session[0]} AND question_id = {question['id']}
        """)).fetchone()
    new_question_text = (
        f"{question_index + 1}/{question_count}"
        + os.linesep
        + os.linesep
        + question[f"text_{user_session[1]}"]
    )
    if user_answer:
        for answer in question['answers']:
            if user_answer[0] == answer['id']:
                new_question_text = (
                    new_question_text
                    + os.linesep
                    + os.linesep
                    + get_constance_value(session, f'BOT_USER_ANSWER_TEXT_{user_session[1].upper()}')
                    + " "
                    + answer[f'text_{user_session[1]}']
                )
                break
    await callback_query.message.edit_text(
        text=new_question_text,
        reply_markup=build_buttons(question_index, user_session[1])
    )


def build_buttons(question_index, language):
    button_rows = []
    for index, answer in enumerate(questions[question_index].get("answers")):
        button_rows.append(
            [InlineKeyboardButton(
                text=answer[f"text_{language}"],
                callback_data=f"set_user_answer_{question_index}_{index}"
            )]
        )
    button_rows.append(
        [
            InlineKeyboardButton(
                text="⬅️",
                callback_data="restart" if question_index == 0 else f"get_question_{question_index - 1}"
            ),
            InlineKeyboardButton(
                text="➡️",
                callback_data="finish" if question_count == question_index + 1 else f"get_question_{question_index + 1}"
            )
        ]
    )
    return InlineKeyboardMarkup(inline_keyboard=button_rows)


@dp.callback_query(F.data.startswith('set_user_answer_'))
async def callback_answer_handler(callback_query: CallbackQuery):
    indexes = callback_query.data.replace('set_user_answer_', '').split("_")
    question_index = int(indexes[0])
    answer_index = int(indexes[1])
    with Session(engine) as session:
        user_session = session.execute(sql.text(f"""
            SELECT id, language
            FROM analytics_diagnosticbotsession
            WHERE message_id = {callback_query.message.message_id}
            ORDER BY id DESC
        """)).fetchone()
        session_id = user_session[0]
        question_id = questions[question_index]['id']
        answer_id = questions[question_index]['answers'][answer_index]['id']
        user_answer = session.execute(sql.text(f"""
            SELECT *
            FROM analytics_diagnosticbotuseranswer
            WHERE session_id = {session_id} AND question_id = {question_id}
            ORDER BY id DESC
        """)).fetchone()
        if user_answer:
            session.execute(sql.text(f"""
                UPDATE analytics_diagnosticbotuseranswer
                SET answer_id = {answer_id}
                WHERE session_id = {session_id} AND question_id = {question_id}
            """))
        else:
            session.execute(sql.text(f"""
                INSERT INTO analytics_diagnosticbotuseranswer (session_id, question_id, answer_id)
                VALUES ({session_id}, {question_id}, {answer_id})
            """))
        session.commit()

    if question_count == question_index + 1:
        await callback_finish_handler(callback_query)
    else:
        next_question_index = question_index + 1
        next_question = questions[next_question_index]
        await callback_query.message.edit_text(
            text=(
                f"{next_question_index + 1}/{question_count}"
                + os.linesep
                + os.linesep
                + next_question[f"text_{user_session[1]}"]
            ),
            reply_markup=build_buttons(next_question_index, user_session[1])
        )


@dp.callback_query(F.data == "restart")
async def callback_restart_handler(callback_query: CallbackQuery):
    with Session(engine) as session:
        await callback_query.message.edit_text(
            text=get_constance_value(session, 'BOT_UNAVAILABLE_TEXT'),
            reply_markup=build_language_buttons()
        )


@dp.callback_query(F.data == "finish")
async def callback_finish_handler(callback_query: CallbackQuery):
    with Session(engine) as session:
        user_language = session.execute(sql.text(f"""
            SELECT language
            FROM analytics_diagnosticbotsession
            WHERE message_id = {callback_query.message.message_id}
        """)).fetchone()
        await callback_query.answer(
            text=get_constance_value(session, f'BOT_FINISH_ALERT_TEXT_{user_language[0].upper()}'),
            show_alert=True
        )
        correct_count = session.execute(sql.text(f"""
            SELECT COUNT(*)
            FROM analytics_diagnosticbotuseranswer a
            JOIN analytics_diagnosticbotsession s ON a.session_id = s.id
            JOIN analytics_diagnosticexamansweroption o ON a.answer_id = o.id
            WHERE s.message_id = {callback_query.message.message_id} AND o.is_correct = true
        """)).fetchone()
        finish_text = get_constance_value(session, f'BOT_SCORE_TEXT_{user_language[0].upper()}')
        await callback_query.message.edit_text(
            text=finish_text.format(correct_count[0]),
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[])
        )
        phone_text = get_constance_value(session, f'BOT_GET_CONTACT_TEXT_{user_language[0].upper()}')
        phone_button_text = get_constance_value(session, f'BOT_GET_CONTACT_BUTTON_TEXT_{user_language[0].upper()}')
        await callback_query.message.answer(phone_text, reply_markup=get_contact_keyboard(phone_button_text))


def get_contact_keyboard(phone_button_text):
    builder = ReplyKeyboardBuilder()
    builder.button(text=phone_button_text, request_contact=True)
    return builder.as_markup()


@dp.message(F.contact)
async def get_contact(message: Message):
    with Session(engine) as session:
        language = session.execute(sql.text(f"""
            SELECT language
            FROM analytics_diagnosticbotsession
            ORDER BY id DESC
        """)).fetchone()
        session.execute(sql.text(f"""
            UPDATE analytics_diagnosticbotsession
            SET phone_number = '{message.contact.phone_number}'
            WHERE user_id = {message.from_user.id}
        """))
        session.commit()
        contact_saved_text = get_constance_value(session, f'BOT_CONTACT_SAVED_TEXT_{language[0].upper()}')
        bye_text = get_constance_value(session, f'BOT_BYE_TEXT_{language[0].upper()}')
    await message.answer(contact_saved_text, reply_markup=ReplyKeyboardRemove())
    button = InlineKeyboardButton(
        text="OkyToky",
        url=get_constance_value(session, f'BOT_CHANNEL_LINK_{language[0].upper()}')
    )
    await message.answer(bye_text, reply_markup=InlineKeyboardMarkup(inline_keyboard=[[button]]))


async def main():
    bot = Bot(TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
