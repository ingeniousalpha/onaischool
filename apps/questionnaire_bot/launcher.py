import asyncio
import asyncpg
import logging
import os
import sys

from aiogram import Dispatcher, Bot, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, Message

TOKEN = os.getenv("QUESTIONNAIRE_BOT_TOKEN")
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
REDIS_AS_CACHE_URL = "redis://{host}:{port}/{db_index}".format(
    host=os.getenv("REDIS_HOST"),
    port=os.getenv("REDIS_PORT"),
    db_index=os.getenv("REDIS_DB_FOR_CACHE"),
)
storage = RedisStorage.from_url(REDIS_AS_CACHE_URL)
dp = Dispatcher(storage=storage)

restart_callback = "restart"
finish_callback = "finish"

texts = {
    "initial": "Тілді таңдаңыз / Выберите язык",
    "language_button": {
        "kk": "Қазақ тілі",
        "ru": "Русский язык"
    },
    "welcome": {
        "kk": "Сәлемдесу мәтіні",
        "ru": "Приветственный текст"
    },
    "welcome_button": {
        "kk": "Сынақты бастау",
        "ru": "Начать тест"
    },
    "finish_alert": {
        "kk": "Сынақ аяқталды",
        "ru": "Тест завершен"
    },
    "user_answer": {
        "kk": "Сіздің жауабыңыз",
        "ru": "Ваш ответ"
    },
    "correct_answer": {
        "kk": "Дұрыс жауап",
        "ru": "Правильный ответ"
    },
    "user_result": {
        "kk": "Сіздің нәтижеңіз",
        "ru": "Ваш результат"
    }

}


class Form(StatesGroup):
    answers = State()


@dp.message(CommandStart())
async def command_start_handler(message: Message, state: FSMContext):
    if message.from_user.is_bot:
        return None
    await get_exam_questions()
    await state.set_state(Form.answers)
    await message.answer(text=texts["initial"], reply_markup=build_language_buttons())


async def get_exam_questions():
    exam_data = []
    pool = await asyncpg.create_pool(
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        host=DB_HOST,
    )
    async with pool.acquire() as connection:
        exam = await connection.fetchrow(
            "SELECT id FROM analytics_diagnosticexam WHERE enabled = true ORDER BY id ASC LIMIT 1"
        )
        if exam:
            exam_questions = await connection.fetch(
                f"SELECT id, title -> 'ru' as text_ru, title -> 'kk' as text_kk "
                f"FROM analytics_diagnosticexamquestion "
                f"WHERE type = 'one_choice' AND diagnostic_exam_id = {exam.get('id')} ORDER BY id ASC"
            )
            for exam_question in exam_questions:
                exam_question_data = {
                    "id": exam_question.get("id"),
                    "text_ru": exam_question.get("text_ru"),
                    "text_kk": exam_question.get("text_kk"),
                    "answers": []
                }
                question_answers = await connection.fetch(
                    f"SELECT id, text -> 'ru' as text_ru, text -> 'kk' as text_kk, is_correct "
                    f"FROM analytics_diagnosticexamansweroption "
                    f"WHERE diagnostic_exam_question_id = {exam_question.get('id')} "
                    f"ORDER BY id ASC"
                )
                for question_answer in question_answers:
                    exam_question_data["answers"].append(
                        {
                            "id": question_answer.get("id"),
                            "text_ru": question_answer.get("text_ru"),
                            "text_kk": question_answer.get("text_kk"),
                            "is_correct": question_answer.get("is_correct")
                        }
                    )
                exam_data.append(exam_question_data)
    await pool.close()
    global questions, question_count
    questions = exam_data
    question_count = len(exam_data)


def build_language_buttons():
    button_rows = [
        [
            InlineKeyboardButton(text=texts["language_button"]["kk"], callback_data="set_language_kk"),
            InlineKeyboardButton(text=texts["language_button"]["ru"], callback_data="set_language_ru")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=button_rows)


@dp.callback_query(F.data.startswith('set_language_'))
async def callback_language_handler(callback_query: CallbackQuery, state: FSMContext):
    language = callback_query.data.replace('set_language_', '')
    data = await state.get_data()
    data[f"{callback_query.message.message_id}"] = {}
    data[f"{callback_query.message.message_id}"]["language"] = language
    await state.set_data(data)
    await callback_query.message.edit_text(text=texts["welcome"][language], reply_markup=build_initial_buttons(language))


def build_initial_buttons(language):
    button_rows = [[InlineKeyboardButton(text=texts["welcome_button"][language], callback_data="get_question_0")]]
    return InlineKeyboardMarkup(inline_keyboard=button_rows)


@dp.callback_query(F.data.startswith('get_question_'))
async def callback_question_handler(callback_query: CallbackQuery, state: FSMContext):
    question_index = int(callback_query.data.replace('get_question_', ''))
    question = questions[question_index]
    data = await state.get_data()
    language = data[f"{callback_query.message.message_id}"]["language"]
    await callback_query.message.edit_text(
        text=f"{question_index + 1}/{question_count}" + os.linesep + os.linesep + question[f"text_{language}"],
        reply_markup=build_buttons(question_index, language)
    )


def build_buttons(question_index, language):
    button_rows = []
    for index, answer in enumerate(questions[question_index].get("answers")):
        button_rows.append(
            [InlineKeyboardButton(text=answer[f"text_{language}"], callback_data=f"set_answer_{question_index}_{index}")]
        )
    button_rows.append(
        [
            InlineKeyboardButton(
                text="⬅️",
                callback_data=restart_callback if question_index == 0 else f"get_question_{question_index - 1}"
            ),
            InlineKeyboardButton(
                text="➡️",
                callback_data=finish_callback if question_count == question_index + 1 else f"get_question_{question_index + 1}"
            )
        ]
    )
    return InlineKeyboardMarkup(inline_keyboard=button_rows)


@dp.callback_query(F.data.startswith('set_answer_'))
async def callback_answer_handler(callback_query: CallbackQuery, state: FSMContext):
    indexes = callback_query.data.replace('set_answer_', '').split("_")
    question_index = int(indexes[0])
    answer_index = int(indexes[1])
    data = await state.get_data()
    language = data[f"{callback_query.message.message_id}"]["language"]
    data[f"{callback_query.message.message_id}"][f"{question_index}"] = answer_index
    await state.set_data(data)

    if question_count == question_index + 1:
        await finish(callback_query, state, language)
    else:
        next_question_index = question_index + 1
        next_question = questions[next_question_index]
        await callback_query.message.edit_text(
            text=(
                f"{next_question_index + 1}/{question_count}"
                + os.linesep
                + os.linesep
                + next_question[f"text_{language}"]
            ),
            reply_markup=build_buttons(next_question_index, language)
        )


@dp.callback_query(F.data == restart_callback)
async def callback_restart_handler(callback_query: CallbackQuery, state: FSMContext):
    await delete_message_data(callback_query, state)
    await callback_query.message.edit_text(text=texts["initial"], reply_markup=build_language_buttons())


@dp.callback_query(F.data == finish_callback)
async def callback_finish_handler(callback_query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    language = data[f"{callback_query.message.message_id}"]["language"]
    await finish(callback_query, state, language)


async def finish(callback_query: CallbackQuery, state: FSMContext, language):
    await callback_query.answer(text=texts["finish_alert"][language], show_alert=True)
    correct_answers = ""
    correct_count = 0
    data = await state.get_data()
    for index, question in enumerate(questions):
        correct_answers = correct_answers + f"{index + 1}) "
        correct_answers = correct_answers + f"{question.get(f'text_{language}')}" + os.linesep + os.linesep
        user_answer_index = data[f"{callback_query.message.message_id}"].get(f"{index}")
        if user_answer_index is not None:
            user_answer = question["answers"][user_answer_index]
        else:
            user_answer = None
        for answer_index, answer in enumerate(question["answers"]):
            if answer["is_correct"]:
                user_answer = user_answer.get(f"text_{language}") if user_answer else '-'
                correct_answers = (
                    correct_answers
                    + f"{texts['user_answer'][language]}: "
                    + user_answer
                    + os.linesep
                    + f"{texts['correct_answer'][language]}: "
                    + answer[f"text_{language}"]
                    + os.linesep
                    + os.linesep
                    + os.linesep
                )

                if user_answer_index is not None and answer_index == int(user_answer_index):
                    correct_count += 1
    correct_answers = correct_answers + texts["user_result"][language] + ": " + f"{correct_count}/{question_count}"
    await callback_query.message.edit_text(text=correct_answers, reply_markup=build_no_buttons())
    await delete_message_data(callback_query, state)


def build_no_buttons():
    return InlineKeyboardMarkup(inline_keyboard=[])


async def delete_message_data(callback_query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    if data.get(f"{callback_query.message.message_id}"):
        del data[f"{callback_query.message.message_id}"]
        await state.set_data(data)


async def main():
    bot = Bot(TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
