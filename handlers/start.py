from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from keyboards.inline import (
    get_language_settings,
    get_level_choice,
    get_voice_settings,
    get_yes_no_keyboard,
    get_start_choice_keyboard
)
from database.models import User
from utils.helpers import update_user_data
from aiogram.enums.parse_mode import ParseMode

router = Router()


@router.message(F.text == "/start")
async def start_command(message: Message, state: FSMContext):
    await message.answer(
        "👋 Добро пожаловать в LEVEL 4 Trainer!\n\n"
        "Давайте начнём с короткой настройки 👇",
        reply_markup=get_language_settings()
    )
    await state.clear()


@router.callback_query(F.data.startswith("lang_"))
async def set_language(callback: CallbackQuery, state: FSMContext):
    lang = callback.data.split("_")[1]
    await state.update_data(language=lang)
    await update_user_data(callback.from_user.id, {"language": lang})

    await callback.message.edit_text(
        "📘 Выберите ваш уровень подготовки ICAO:",
        reply_markup=get_level_choice()
    )


@router.callback_query(F.data.startswith("level_"))
async def set_level(callback: CallbackQuery, state: FSMContext):
    level = int(callback.data.split("_")[1])
    await state.update_data(level=level)
    await update_user_data(callback.from_user.id, {"level": level})

    await callback.message.edit_text(
        f"🔊 Настроим озвучку вопросов?",
        reply_markup=get_voice_settings("question")
    )


@router.callback_query(F.data.in_({"voice_q_on", "voice_q_off"}))
async def set_voice_question(callback: CallbackQuery, state: FSMContext):
    voice_q = callback.data.endswith("on")
    await state.update_data(voice_question=voice_q)
    await update_user_data(callback.from_user.id, {"voice_question": voice_q})

    await callback.message.edit_text(
        "🔊 Настроим озвучку ответов?",
        reply_markup=get_voice_settings("answer")
    )


@router.callback_query(F.data.in_({"voice_a_on", "voice_a_off"}))
async def set_voice_answer(callback: CallbackQuery, state: FSMContext):
    voice_a = callback.data.endswith("on")
    await state.update_data(voice_answer=voice_a)
    await update_user_data(callback.from_user.id, {"voice_answer": voice_a})

    await callback.message.edit_text(
        "❓ Подключить вопрос дня?",
        reply_markup=get_yes_no_keyboard("question_day")
    )


@router.callback_query(F.data.in_({"question_day_yes", "question_day_no"}))
async def set_question_day(callback: CallbackQuery, state: FSMContext):
    question_day = callback.data.endswith("yes")
    await state.update_data(question_day=question_day)
    await update_user_data(callback.from_user.id, {"question_day": question_day})

    await callback.message.edit_text(
        "💡 Подключить совет дня?",
        reply_markup=get_yes_no_keyboard("tip_day")
    )


@router.callback_query(F.data.in_({"tip_day_yes", "tip_day_no"}))
async def set_tip_day(callback: CallbackQuery, state: FSMContext):
    tip_day = callback.data.endswith("yes")
    data = await state.get_data()
    await update_user_data(callback.from_user.id, {
        "tip_day": tip_day,
        "onboarding_complete": True
    })

    lang = data.get("language", "ru")
    text = {
        "ru": "🎯 Настройка завершена!\n\nВыберите, с чего хотите начать:",
        "en": "🎯 Setup complete!\n\nChoose where to start:"
    }[lang]

    await callback.message.edit_text(
        text,
        reply_markup=get_start_choice_keyboard(lang),
        parse_mode=ParseMode.HTML
    )
