# handlers/exam.py
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from sqlalchemy import select
from database.db import async_session
from database.models import User
from services.gpt import analyze_exam_voice, analyze_emergency_response
from services.access import check_exam_limit, register_exam_attempt
from keyboards.inline import get_exam_stage_buttons, get_exam_start_button

router = Router()
exam_stage = {}


@router.message(F.text.lower() == "🎤 экзамен")
async def enter_exam(message: Message):
    user_id = message.from_user.id

    async with async_session() as session:
        user = (await session.execute(select(User).where(User.telegram_id == user_id))).scalar()

        if not await check_exam_limit(user):
            await message.answer("⛔️ Лимит экзаменов исчерпан. Повторите позже или оформите подписку.")
            return

    exam_stage[user_id] = 1
    await message.answer(
        "🎓 Экзамен состоит из трёх этапов:\n\n"
        "1. Кратко расскажите о себе\n"
        "2. Ответьте на вопросы по авиации\n"
        "3. Передайте сообщение при нештатной ситуации\n\n"
        "📌 Рекомендуем пройти обучение и тренировку перед экзаменом.",
        reply_markup=get_exam_start_button()
    )


@router.callback_query(F.data == "start_exam")
async def start_exam(callback: CallbackQuery):
    user_id = callback.from_user.id
    exam_stage[user_id] = 1
    await callback.message.answer("🗣 Расскажите о себе (на английском). Запишите голосовое сообщение.")
    await callback.answer()


@router.message(F.voice)
async def process_voice_exam(message: Message):
    user_id = message.from_user.id
    stage = exam_stage.get(user_id, 1)

    if stage == 1:
        await message.answer("🧠 Анализируем рассказ о себе...")
        result = await analyze_exam_voice(message.voice, user_id)
        await message.answer(f"📊 Результат: {result}")
        exam_stage[user_id] = 2
        await message.answer("❓ Вопрос по авиации. Запишите голосовой ответ.")
        return

    elif stage == 2:
        await message.answer("🧠 Анализируем ответ на вопрос...")
        result = await analyze_exam_voice(message.voice, user_id)
        await message.answer(f"📊 Результат: {result}")
        exam_stage[user_id] = 3
        await message.answer("🚨 Ситуация: Пассажиру стало плохо, у него рвота. Что вы доложите диспетчеру? (На английском)")
        return

    elif stage == 3:
        await message.answer("🧠 Анализируем аварийную ситуацию...")
        level, feedback = await analyze_emergency_response(message.voice, user_id)
        await message.answer(f"📊 Финальный уровень: {level}\n\n📝 Комментарий:\n{feedback}")
        await register_exam_attempt(user_id)
        del exam_stage[user_id]

        await message.answer(
            "🎉 Экзамен завершён!\n\n"
            "📌 Вы можете пройти экзамен снова при наличии доступных попыток или оформите подписку для увеличения лимита."
        )
