# handlers/exam.py
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from keyboards.inline import get_exam_start_button, get_exam_next_step_button
from services.gpt import analyze_exam_response
from database.db import async_session
from database.models import UserProgress
from utils.helpers import get_user_level

router = Router()

user_exam_state = {}  # {user_id: {'step': int, 'answers': []}}


@router.message(F.text.lower() == "🎤 экзамен")
async def exam_entry(message: Message):
    user_id = message.from_user.id
    user_exam_state[user_id] = {"step": 0, "answers": []}

    await message.answer(
        "🎤 Вы вошли в режим экзамена.\n\n"
        "Экзамен состоит из 3 этапов:\n"
        "1. Краткий рассказ о себе\n"
        "2. Ответы на экзаменационные вопросы\n"
        "3. Передача сообщения о нештатной ситуации\n\n"
        "Рекомендуется пройти обучение, тренировку и отработку аварийных ситуаций перед началом.",
        reply_markup=get_exam_start_button()
    )


@router.callback_query(F.data == "start_exam")
async def start_exam(callback: CallbackQuery):
    user_id = callback.from_user.id
    user_exam_state[user_id]["step"] = 1
    await callback.message.answer("👤 Этап 1: Расскажите о себе (на английском). Отправьте голосовое сообщение.")
    await callback.answer()


@router.message(F.voice, F.chat.type == "private")
async def process_exam_voice(message: Message):
    user_id = message.from_user.id
    if user_id not in user_exam_state:
        await message.answer("Пожалуйста, сначала запустите экзамен с команды 🎤 Экзамен.")
        return

    step = user_exam_state[user_id]["step"]
    file_id = message.voice.file_id
    user_exam_state[user_id]["answers"].append((step, file_id))

    if step == 1:
        user_exam_state[user_id]["step"] = 2
        await message.answer("📋 Этап 2: Ответьте на следующие вопросы (озвучка + голосовой ответ).\n(пример вопроса будет позже)")
    elif step == 2:
        user_exam_state[user_id]["step"] = 3
        await message.answer("🚨 Этап 3: Вам поступил случай:\n'Passenger has severe nausea and vomiting. What will you report to ATC?'\nОтветьте голосом.")
    elif step == 3:
        await message.answer("🎯 Экзамен завершён. Идёт анализ...")

        level = await get_user_level(user_id)
        score = await analyze_exam_response(user_id, level, user_exam_state[user_id]["answers"])

        async with async_session() as session:
            progress = UserProgress(user_id=user_id, exam_score=score)
            session.add(progress)
            await session.commit()

        await message.answer(
            f"✅ Экзамен завершён.\n\n📊 Ваш уровень по шкале ICAO: {score}\n\n"
            "Вы можете пройти экзамен снова позже или вернуться к обучению и тренировке.",
            reply_markup=get_exam_next_step_button()
        )

        del user_exam_state[user_id]
