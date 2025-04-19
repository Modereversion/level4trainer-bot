# handlers/learning.py
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from database.db import async_session
from database.models import Lesson, UserProgress
from keyboards.inline import get_learning_buttons, get_learning_after_buttons, get_learning_topic_buttons
from utils.helpers import get_user_language, get_user_level

router = Router()

user_learning_state = {}  # {user_id: {'lesson_id': int}}


@router.message(F.text == "📚 Обучение")
async def enter_learning(message: Message):
    user_id = message.from_user.id
    lang = await get_user_language(user_id)
    level = await get_user_level(user_id)

    async with async_session() as session:
        result = await session.execute(
            Lesson.__table__.select().where(Lesson.level == level)
        )
        lessons = result.fetchall()

    if not lessons:
        await message.answer("Нет доступных уроков.")
        return

    lesson = lessons[0]
    user_learning_state[user_id] = {"lesson_id": lesson.id}
    await message.answer(
        f"📘 {lesson.title}\n\n{lesson.content}",
        reply_markup=get_learning_buttons()
    )


@router.callback_query(F.data == "next_lesson")
async def next_lesson(callback: CallbackQuery):
    user_id = callback.from_user.id
    current_id = user_learning_state.get(user_id, {}).get("lesson_id")

    async with async_session() as session:
        result = await session.execute(
            Lesson.__table__.select().where(Lesson.id > current_id).order_by(Lesson.id.asc())
        )
        next_lesson = result.first()

    if next_lesson:
        user_learning_state[user_id]["lesson_id"] = next_lesson.id
        await callback.message.edit_text(
            f"📘 {next_lesson.title}\n\n{next_lesson.content}",
            reply_markup=get_learning_buttons()
        )
    else:
        await callback.message.edit_text("✅ Вы завершили обучение.", reply_markup=get_learning_after_buttons())
    await callback.answer()


@router.callback_query(F.data == "prev_lesson")
async def previous_lesson(callback: CallbackQuery):
    user_id = callback.from_user.id
    current_id = user_learning_state.get(user_id, {}).get("lesson_id")

    async with async_session() as session:
        result = await session.execute(
            Lesson.__table__.select().where(Lesson.id < current_id).order_by(Lesson.id.desc())
        )
        prev_lesson = result.first()

    if prev_lesson:
        user_learning_state[user_id]["lesson_id"] = prev_lesson.id
        await callback.message.edit_text(
            f"📘 {prev_lesson.title}\n\n{prev_lesson.content}",
            reply_markup=get_learning_buttons()
        )
    else:
        await callback.answer("Это первый урок.")


@router.callback_query(F.data == "choose_topic")
async def choose_learning_topic(callback: CallbackQuery):
    await callback.message.edit_text(
        "📂 Выберите тему:",
        reply_markup=get_learning_topic_buttons()
    )
    await callback.answer()


@router.callback_query(F.data.startswith("topic_"))
async def show_topic(callback: CallbackQuery):
    topic_id = int(callback.data.split("_")[1])
    user_id = callback.from_user.id

    async with async_session() as session:
        lesson = await session.get(Lesson, topic_id)

    if lesson:
        user_learning_state[user_id] = {"lesson_id": lesson.id}
        await callback.message.edit_text(
            f"📘 {lesson.title}\n\n{lesson.content}",
            reply_markup=get_learning_buttons()
        )
    else:
        await callback.message.edit_text("Урок не найден.")
    await callback.answer()
