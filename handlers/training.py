# handlers/training.py
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from sqlalchemy import select
from database.db import async_session
from database.models import User, Question
from keyboards.inline import get_training_buttons, get_after_training_buttons
from services.tts import delete_previous_voice, send_tts
from utils.helpers import get_random_question, mark_question_done, get_user_progress, get_unanswered_questions

router = Router()
user_last_question = {}


@router.message(F.text.lower() == "🚀 тренировка")
async def training_entry(message: Message):
    user_id = message.from_user.id
    async with async_session() as session:
        user = (await session.execute(select(User).where(User.telegram_id == user_id))).scalar()
        questions = await get_unanswered_questions(user_id, user.level)
        if not questions:
            await message.answer(
                "✅ Вы завершили тренировку уровня 4." if user.level == "level_4" else "✅ Вы завершили тренировку уровня 5.",
                reply_markup=get_after_training_buttons(user.level)
            )
            return

        question = questions[0]
        user_last_question[user_id] = question.id

        await delete_previous_voice(user_id)
        await message.answer(f"❓ {question.text_en}", reply_markup=get_training_buttons())
        if user.voice_enabled:
            await send_tts(user_id, question.text_en)


@router.callback_query(F.data == "next_question")
async def next_question(callback: CallbackQuery):
    user_id = callback.from_user.id
    async with async_session() as session:
        user = (await session.execute(select(User).where(User.telegram_id == user_id))).scalar()
        questions = await get_unanswered_questions(user_id, user.level)
        if not questions:
            await callback.message.edit_text(
                "✅ Вы завершили тренировку уровня 4." if user.level == "level_4" else "✅ Вы завершили тренировку уровня 5.",
                reply_markup=get_after_training_buttons(user.level)
            )
            return

        question = questions[0]
        user_last_question[user_id] = question.id

        await delete_previous_voice(user_id)
        await callback.message.edit_text(f"❓ {question.text_en}", reply_markup=get_training_buttons())
        if user.voice_enabled:
            await send_tts(user_id, question.text_en)
        await callback.answer()


@router.callback_query(F.data == "show_answer")
async def show_answer(callback: CallbackQuery):
    user_id = callback.from_user.id
    async with async_session() as session:
        question_id = user_last_question.get(user_id)
        if question_id:
            question = await session.get(Question, question_id)
            await callback.message.edit_text(f"✅ {question.answer_en}", reply_markup=get_training_buttons(answer=True))
            if (await session.get(User, user_id)).answer_enabled:
                await send_tts(user_id, question.answer_en)
        await callback.answer()


@router.callback_query(F.data == "translate_question")
async def translate_question(callback: CallbackQuery):
    user_id = callback.from_user.id
    async with async_session() as session:
        question_id = user_last_question.get(user_id)
        if question_id:
            question = await session.get(Question, question_id)
            await delete_previous_voice(user_id)
            await callback.message.edit_text(f"🌐 {question.text_ru}", reply_markup=get_training_buttons(translation=True))
        await callback.answer()


@router.callback_query(F.data == "translate_answer")
async def translate_answer(callback: CallbackQuery):
    user_id = callback.from_user.id
    async with async_session() as session:
        question_id = user_last_question.get(user_id)
        if question_id:
            question = await session.get(Question, question_id)
            await delete_previous_voice(user_id)
            await callback.message.edit_text(f"🌐 {question.answer_ru}", reply_markup=get_training_buttons(translation=True, answer=True))
        await callback.answer()


@router.callback_query(F.data == "previous_question")
async def previous_question(callback: CallbackQuery):
    user_id = callback.from_user.id
    async with async_session() as session:
        question_id = user_last_question.get(user_id)
        if question_id:
            question = await session.get(Question, question_id)
            await callback.message.answer(f"↩️ {question.text_en}", reply_markup=get_training_buttons())
            if (await session.get(User, user_id)).voice_enabled:
                await send_tts(user_id, question.text_en)
        await callback.answer()
