# handlers/learning.py
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from keyboards.inline import get_lesson_navigation, get_after_learning_buttons
from database.db import async_session
from database.models import Lesson
from sqlalchemy import select

router = Router()


@router.message(F.text.lower() == "📚 обучение")
async def enter_learning(message: Message):
    # Показываем вступительное сообщение
    await message.answer(
        "📚 Вы вошли в раздел обучения.\n\n"
        "Изучайте грамматические и лексические темы, соответствующие уровню ICAO 4 или 5.\n"
        "Рекомендуется пройти все темы перед тренировкой и экзаменом.",
    )
    await show_lesson(message, 1)


async def show_lesson(message: Message, lesson_id: int):
    async with async_session() as session:
        lesson = await session.scalar(select(Lesson).where(Lesson.id == lesson_id))
        if lesson:
            text = f"📘 {lesson.title}\n\n{lesson.content}"
            await message.answer(
                text,
                reply_markup=get_lesson_navigation(lesson.id)
            )
        else:
            await message.answer("Урок не найден.")


@router.callback_query(F.data.startswith("lesson_"))
async def lesson_navigation(callback: CallbackQuery):
    action, lesson_id = callback.data.split("_")
    lesson_id = int(lesson_id)

    if action == "lesson":
        await show_lesson(callback.message, lesson_id)
    elif action == "next":
        await show_lesson(callback.message, lesson_id + 1)
    elif action == "prev" and lesson_id > 1:
        await show_lesson(callback.message, lesson_id - 1)
    await callback.answer()
