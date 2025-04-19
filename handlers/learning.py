# handlers/learning.py
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from sqlalchemy import select
from database.db import async_session
from database.models import Lesson, User
from keyboards.inline import get_learning_buttons, get_after_learning_buttons, get_topic_selection_keyboard
from utils.helpers import get_user_lesson_state, update_user_lesson_state, get_lessons_by_level

router = Router()
user_last_lesson = {}


@router.message(F.text.lower() == "📚 обучение")
async def enter_learning(message: Message):
    user_id = message.from_user.id
    async with async_session() as session:
        user = (await session.execute(select(User).where(User.telegram_id == user_id))).scalar()
        lessons = await get_lessons_by_level(user.level)

        if not lessons:
            await message.answer("❌ Уроки не найдены.")
            return

        last_index = await get_user_lesson_state(user_id)
        lesson = lessons[last_index] if last_index < len(lessons) else lessons[0]

        user_last_lesson[user_id] = lesson.id
        await message.answer(f"📘 {lesson.title}\n\n{lesson.content}", reply_markup=get_learning_buttons())


@router.callback_query(F.data == "next_lesson")
async def next_lesson(callback: CallbackQuery):
    user_id = callback.from_user.id
    async with async_session() as session:
        user = (await session.execute(select(User).where(User.telegram_id == user_id))).scalar()
        lessons = await get_lessons_by_level(user.level)

        current_index = await get_user_lesson_state(user_id)
        next_index = current_index + 1 if current_index + 1 < len(lessons) else 0
        await update_user_lesson_state(user_id, next_index)

        lesson = lessons[next_index]
        user_last_lesson[user_id] = lesson.id
        await callback.message.edit_text(f"📘 {lesson.title}\n\n{lesson.content}", reply_markup=get_learning_buttons())
        await callback.answer()


@router.callback_query(F.data == "prev_lesson")
async def prev_lesson(callback: CallbackQuery):
    user_id = callback.from_user.id
    async with async_session() as session:
        user = (await session.execute(select(User).where(User.telegram_id == user_id))).scalar()
        lessons = await get_lessons_by_level(user.level)

        current_index = await get_user_lesson_state(user_id)
        prev_index = current_index - 1 if current_index > 0 else len(lessons) - 1
        await update_user_lesson_state(user_id, prev_index)

        lesson = lessons[prev_index]
        user_last_lesson[user_id] = lesson.id
        await callback.message.edit_text(f"📘 {lesson.title}\n\n{lesson.content}", reply_markup=get_learning_buttons())
        await callback.answer()


@router.callback_query(F.data == "select_topic")
async def show_topics(callback: CallbackQuery):
    async with async_session() as session:
        user = (await session.execute(select(User).where(User.telegram_id == callback.from_user.id))).scalar()
        lessons = await get_lessons_by_level(user.level)
        await callback.message.edit_text("📂 Выберите тему:", reply_markup=get_topic_selection_keyboard(lessons))
        await callback.answer()


@router.callback_query(F.data.startswith("topic_"))
async def select_topic(callback: CallbackQuery):
    topic_id = int(callback.data.split("_")[1])
    async with async_session() as session:
        lesson = await session.get(Lesson, topic_id)
        await update_user_lesson_state(callback.from_user.id, topic_id - 1)
        user_last_lesson[callback.from_user.id] = lesson.id
        await callback.message.edit_text(f"📘 {lesson.title}\n\n{lesson.content}", reply_markup=get_learning_buttons())
        await callback.answer()
