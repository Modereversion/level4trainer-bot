# handlers/start.py
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from sqlalchemy import select
from database.db import async_session
from database.models import User
from keyboards.reply import get_main_menu
from keyboards.inline import get_initial_language_buttons, get_level_selection_buttons, get_voice_prompt_buttons, get_daily_settings_buttons
from utils.helpers import get_user_language

router = Router()


@router.message(F.text == "/start")
async def start_command(message: Message):
    user_id = message.from_user.id
    full_name = message.from_user.full_name
    username = message.from_user.username
    language_code = message.from_user.language_code

    async with async_session() as session:
        result = await session.execute(select(User).where(User.telegram_id == user_id))
        user = result.scalar_one_or_none()

        if not user:
            user = User(
                telegram_id=user_id,
                full_name=full_name,
                username=username,
                language=language_code if language_code in ["ru", "en"] else "en"
            )
            session.add(user)
            await session.commit()
            await message.answer("👋 Добро пожаловать! Давайте настроим бота.", reply_markup=get_initial_language_buttons())
        else:
            await message.answer("👋 С возвращением!", reply_markup=get_main_menu(language_code))


@router.callback_query(F.data.startswith("lang_"))
async def select_language(callback: CallbackQuery):
    lang = callback.data.split("_")[1]
    user_id = callback.from_user.id

    async with async_session() as session:
        result = await session.execute(select(User).where(User.telegram_id == user_id))
        user = result.scalar_one_or_none()
        if user:
            user.language = lang
            await session.commit()

    await callback.message.edit_text("Выберите уровень сложности:", reply_markup=get_level_selection_buttons(lang))
    await callback.answer()


@router.callback_query(F.data.startswith("level_"))
async def select_level(callback: CallbackQuery):
    level = callback.data.split("_")[1]
    user_id = callback.from_user.id

    async with async_session() as session:
        result = await session.execute(select(User).where(User.telegram_id == user_id))
        user = result.scalar_one_or_none()
        if user:
            user.level = f"level_{level}"
            await session.commit()

    await callback.message.edit_text("Включить озвучку вопросов и ответов?", reply_markup=get_voice_prompt_buttons())
    await callback.answer()


@router.callback_query(F.data.startswith("voice_"))
async def voice_toggle(callback: CallbackQuery):
    option = callback.data.split("_")[1]
    user_id = callback.from_user.id
    voice_enabled = option == "on"

    async with async_session() as session:
        result = await session.execute(select(User).where(User.telegram_id == user_id))
        user = result.scalar_one_or_none()
        if user:
            user.voice_enabled = voice_enabled
            user.answer_enabled = voice_enabled
            await session.commit()

    await callback.message.edit_text("Хотите получать вопрос дня и совет дня?", reply_markup=get_daily_settings_buttons())
    await callback.answer()


@router.callback_query(F.data.startswith("daily_"))
async def set_daily(callback: CallbackQuery):
    action = callback.data.split("_")[1]
    user_id = callback.from_user.id

    async with async_session() as session:
        user = await session.get(User, user_id)
        if action == "qon":
            user.question_of_the_day = True
        elif action == "qoff":
            user.question_of_the_day = False
        elif action == "ton":
            user.tip_of_the_day = True
        elif action == "toff":
            user.tip_of_the_day = False
        await session.commit()

    await callback.message.answer("✅ Настройка завершена!", reply_markup=get_main_menu(user.language))
    await callback.answer()
