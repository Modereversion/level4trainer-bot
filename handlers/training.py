# handlers/training.py
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from sqlalchemy import select
from random import choice
from database.db import async_session
from database.models import Question
from keyboards.inline import (
    get_training_buttons,
    get_after_level_buttons,
)
from utils.helpers import get_user_level, save_progress

router = Router()

user_questions_cache = {}  # {user_id: [question_ids]}


@router.message(F.text.lower() == "🚀 тренировка")
async def start_training(message: Message):
    await message.answer(
        "🚀 Вы начали тренировку.\n"
        "Вам будут предложены вопросы для подготовки к устной части ICAO.\n"
        "Вы можете просматривать ответы, переводы и откладывать сложные вопросы.",
    )
    await send_random_question(message)


async def send_random_question(message: Message):
    user_id = message.from_user.id
    level = await get_user_level(user_id)

    async with async_session() as session:
        query = select(Question).where(Question.level == level)
        all_questions = (await session.scalars(query)).all()

        if not all_questions:
            await message.answer("Вопросы не найдены для вашего уровня.")
            return

        if user_id not in user_questions_cache:
            user_questions_cache[user_id] = []

        available = [q for q in all_questions if q.id not in user_questions_cache[user_id]]
        if not available:
            await message.answer(
                f"🎉 Вы завершили тренировку уровня {level.upper()}!",
                reply_markup=get_after_level_buttons(level)
            )
            return

        question = choice(available)
        user_questions_cache[user_id].append(question.id)

        await save_progress(user_id, question_id=question.id)

        await message.answer(
            f"❓ {question.text_en}",
            reply_markup=get_training_buttons(question.id)
        )


@router.callback_query(F.data.startswith("answer_"))
async def show_answer(callback: CallbackQuery):
    _, qid = callback.data.split("_")
    qid = int(qid)
    async with async_session() as session:
        question = await session.get(Question, qid)
        if question:
            await callback.message.edit_text(
                f"✅ {question.text_en}\n\n💬 {question.answer_en}",
                reply_markup=get_training_buttons(qid)
            )
    await callback.answer()


@router.callback_query(F.data.startswith("translateq_"))
async def translate_question(callback: CallbackQuery):
    _, qid = callback.data.split("_")
    qid = int(qid)
    async with async_session() as session:
        question = await session.get(Question, qid)
        if question:
            await callback.message.edit_text(
                f"❓ {question.text_ru}",
                reply_markup=get_training_buttons(qid, translated_q=True)
            )
    await callback.answer()


@router.callback_query(F.data.startswith("translatea_"))
async def translate_answer(callback: CallbackQuery):
    _, qid = callback.data.split("_")
    qid = int(qid)
    async with async_session() as session:
        question = await session.get(Question, qid)
        if question:
            await callback.message.edit_text(
                f"❓ {question.text_ru}\n\n💬 {question.answer_ru}",
                reply_markup=get_training_buttons(qid, translated_q=True, translated_a=True)
            )
    await callback.answer()


@router.callback_query(F.data == "next_question")
async def next_question(callback: CallbackQuery):
    await send_random_question(callback.message)
    await callback.answer()


@router.callback_query(F.data == "back_to_previous")
async def previous_question(callback: CallbackQuery):
    # Поведение возврата реализуется отдельно, если включено
    await callback.answer("⏪ Возврат к предыдущему пока недоступен.", show_alert=True)
