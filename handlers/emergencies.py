# handlers/emergencies.py
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from sqlalchemy import select
from database.db import async_session
from database.models import EmergencyCase, User
from keyboards.inline import get_emergency_case_buttons, get_emergency_next_buttons
from services.gpt import analyze_emergency_response
from services.access import check_emergency_limit, register_emergency_attempt
from utils.helpers import get_emergency_cases_by_language

router = Router()
active_cases = {}


@router.message(F.text.lower() == "🚨 аварийные ситуации")
async def enter_emergencies(message: Message):
    user_id = message.from_user.id

    async with async_session() as session:
        user = (await session.execute(select(User).where(User.telegram_id == user_id))).scalar()

        if not await check_emergency_limit(user):
            await message.answer("⛔️ Лимит попыток для отработки аварийных ситуаций исчерпан. Повторите позже или оформите подписку.")
            return

        cases = await get_emergency_cases_by_language(user.language)

        if not cases:
            await message.answer("❌ Кейсы не найдены.")
            return

        case = cases[0]
        active_cases[user_id] = case.id

        await message.answer(
            f"📍 Ситуация:\n\n{case.text_ru if user.language == 'ru' else case.text_en}",
            reply_markup=get_emergency_case_buttons(user.language)
        )


@router.callback_query(F.data == "example_answer")
async def show_example(callback: CallbackQuery):
    user_id = callback.from_user.id
    case_id = active_cases.get(user_id)

    if not case_id:
        await callback.answer("⛔️ Сначала выберите кейс.")
        return

    async with async_session() as session:
        case = await session.get(EmergencyCase, case_id)
        answer = case.sample_answer_en or "No example available."
        await callback.message.answer(f"📝 Пример ответа:\n\n{answer}")
        await callback.answer()


@router.callback_query(F.data == "emergency_voice_answer")
async def request_voice(callback: CallbackQuery):
    await callback.message.answer("🎤 Пожалуйста, запишите свой ответ голосом на английском.")
    await callback.answer()


@router.message(F.voice)
async def handle_voice(message: Message):
    user_id = message.from_user.id
    case_id = active_cases.get(user_id)

    if not case_id:
        return await message.answer("⛔️ Нет активного кейса. Сначала выберите ситуацию.")

    # Анализ ответа
    await message.answer("🧠 Анализируем ваш ответ...")

    level, feedback = await analyze_emergency_response(message.voice, user_id)

    await message.answer(f"📊 Оценка уровня: {level}\n\n📝 Комментарий:\n{feedback}")
    await register_emergency_attempt(user_id)

    await message.answer("Хотите попробовать другую ситуацию?", reply_markup=get_emergency_next_buttons())


@router.callback_query(F.data == "next_emergency_case")
async def next_case(callback: CallbackQuery):
    user_id = callback.from_user.id
    async with async_session() as session:
        user = (await session.execute(select(User).where(User.telegram_id == user_id))).scalar()
        cases = await get_emergency_cases_by_language(user.language)
        if not cases:
            await callback.message.answer("❌ Кейсы не найдены.")
            return

        next_case = cases[1 % len(cases)]
        active_cases[user_id] = next_case.id
        await callback.message.answer(
            f"📍 Ситуация:\n\n{next_case.text_ru if user.language == 'ru' else next_case.text_en}",
            reply_markup=get_emergency_case_buttons(user.language)
        )
        await callback.answer()
