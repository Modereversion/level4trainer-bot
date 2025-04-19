from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.filters import CommandStart
from keyboards.inline import get_language_settings, get_voice_settings, get_main_menu
from database.models import User, Progress
from database.db import SessionLocal
from services.access import create_user_if_not_exists

router = Router()

@router.message(CommandStart())
async def start_bot(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "👋 Добро пожаловать в *LEVEL 4 Trainer* — бот для подготовки к устной части экзамена ICAO.",
        reply_markup=None,
        parse_mode="Markdown"
    )

    await create_user_if_not_exists(message.from_user)
    await message.answer("🌍 Выберите язык интерфейса:", reply_markup=get_language_settings())

@router.callback_query(F.data.startswith("lang_"))
async def set_language(callback: CallbackQuery, state: FSMContext):
    lang = callback.data.split("_")[1]
    await state.update_data(language=lang)
    await callback.message.edit_text("🎯 На какой уровень вы претендуете?")
    await callback.message.edit_reply_markup(get_level_choice())

@router.callback_query(F.data.startswith("level_"))
async def set_level(callback: CallbackQuery, state: FSMContext):
    level = callback.data.split("_")[1]
    await state.update_data(level=level)
    await callback.message.edit_text("🔊 Включить озвучку вопросов?")
    await callback.message.edit_reply_markup(get_voice_settings(step="question"))

@router.callback_query(F.data.startswith("voice_q_"))
async def set_question_voice(callback: CallbackQuery, state: FSMContext):
    enabled = callback.data.split("_")[2] == "on"
    await state.update_data(voice_questions=enabled)
    await callback.message.edit_text("🎧 Включить озвучку ответов?")
    await callback.message.edit_reply_markup(get_voice_settings(step="answer"))

@router.callback_query(F.data.startswith("voice_a_"))
async def set_answer_voice(callback: CallbackQuery, state: FSMContext):
    enabled = callback.data.split("_")[2] == "on"
    await state.update_data(voice_answers=enabled)
    await callback.message.edit_text("❓ Получать *вопрос дня*?")
    await callback.message.edit_reply_markup(get_yes_no_keyboard("daily_q"))

@router.callback_query(F.data.startswith("daily_q_"))
async def set_daily_question(callback: CallbackQuery, state: FSMContext):
    enabled = callback.data.split("_")[2] == "yes"
    await state.update_data(daily_question=enabled)
    await callback.message.edit_text("💡 Получать *совет дня*?")
    await callback.message.edit_reply_markup(get_yes_no_keyboard("daily_tip"))

@router.callback_query(F.data.startswith("daily_tip_"))
async def finish_setup(callback: CallbackQuery, state: FSMContext):
    enabled = callback.data.split("_")[2] == "yes"
    data = await state.get_data()
    data["daily_tip"] = enabled

    # Обновляем пользователя в базе
    async with SessionLocal() as session:
        user = await session.get(User, callback.from_user.id)
        if user:
            user.language_code = data.get("language", "ru")
            user.level = data.get("level", "4")
            user.voice_enabled = data.get("voice_questions", True)
            user.answer_voice_enabled = data.get("voice_answers", True)
            user.question_of_day = data.get("daily_question", False)
            user.tip_of_day = data.get("daily_tip", False)
            await session.commit()

    await callback.message.edit_text("✅ Настройка завершена!")
    await callback.message.answer(
        "📚 Рекомендуется начать с обучения или сразу перейти к тренировке:",
        reply_markup=get_start_choice_keyboard(data.get("language", "ru"))
    )
