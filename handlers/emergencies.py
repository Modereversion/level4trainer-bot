# handlers/emergencies.py
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from keyboards.inline import get_emergency_case_buttons, get_continue_emergency_buttons
from services.gpt import analyze_emergency_response
from database.db import async_session
from database.models import EmergencyCase, UserProgress
from utils.helpers import get_user_language, get_user_level

router = Router()

user_emergency_state = {}  # {user_id: {'case_id': int, 'attempt': int}}


@router.message(F.text == "🚨 Аварийные ситуации")
async def emergency_entry(message: Message):
    user_id = message.from_user.id
    lang = await get_user_language(user_id)

    if lang == 'ru':
        intro = (
            "Вы вошли в раздел 🚨 Аварийные ситуации.\n\n"
            "Здесь вы будете тренироваться в передаче сообщений о внештатных ситуациях диспетчеру. "
            "Это один из самых важных разделов — вы будете отвечать голосом, а ИИ проанализирует ваш ответ. "
            "Каждая ситуация уникальна, и вы можете получить до 3 попыток на ответ.\n\n"
            "🧑‍✈️ Вам доступно определённое количество кейсов в 12 часов.\n"
            "Чтобы увеличить лимит — оформите подписку или запросите доступ."
        )
    else:
        intro = (
            "You have entered the 🚨 Emergency Situations section.\n\n"
            "Here you will practice reporting emergency situations to ATC. "
            "This is one of the most important parts — you will answer by voice, and AI will analyze your response. "
            "Each scenario is unique, and you have up to 3 attempts per case.\n\n"
            "🧑‍✈️ You have a limited number of cases in 12 hours.\n"
            "To increase the limit — subscribe or request access."
        )

    await message.answer(intro, reply_markup=get_continue_emergency_buttons())


@router.callback_query(F.data == "start_emergency")
async def start_emergency_case(callback: CallbackQuery):
    user_id = callback.from_user.id
    level = await get_user_level(user_id)
    lang = await get_user_language(user_id)

    async with async_session() as session:
        cases = await session.execute(
            EmergencyCase.__table__.select()
        )
        all_cases = cases.fetchall()

    if not all_cases:
        await callback.message.answer("Нет доступных кейсов.")
        return

    case = all_cases[0]  # в будущем добавить случайность и проверку пройденных
    user_emergency_state[user_id] = {"case_id": case.id, "attempt": 1}

    text = case.text_ru if lang == 'ru' else case.text_en
    await callback.message.answer(f"⚠️ Ситуация:\n{text}", reply_markup=get_emergency_case_buttons())
    await callback.answer()


@router.callback_query(F.data == "example_answer")
async def show_sample_answer(callback: CallbackQuery):
    user_id = callback.from_user.id
    lang = await get_user_language(user_id)

    async with async_session() as session:
        case_id = user_emergency_state.get(user_id, {}).get("case_id")
        case = await session.get(EmergencyCase, case_id)

    answer = case.sample_answer_en if case else "Sample answer not found."
    await callback.message.answer(f"💬 Пример ответа:\n{answer}")
    await callback.answer()


@router.message(F.voice)
async def handle_emergency_voice(message: Message):
    user_id = message.from_user.id
    case_state = user_emergency_state.get(user_id)

    if not case_state:
        await message.answer("Сначала выберите кейс.")
        return

    attempt = case_state["attempt"]
    file_id = message.voice.file_id
    level = await get_user_level(user_id)

    score, passed = await analyze_emergency_response(file_id, level)

    if passed:
        await message.answer(f"✅ Ответ принят. Уровень: {score}\nГотовы к следующей ситуации?")
        del user_emergency_state[user_id]
    else:
        if attempt < 3:
            user_emergency_state[user_id]["attempt"] += 1
            await message.answer("❌ Ответ не принят. Попробуйте ещё раз.")
        else:
            await message.answer("❌ Все попытки исчерпаны. Попробуйте другой кейс или вернитесь к обучению.")
            del user_emergency_state[user_id]
