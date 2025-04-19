# handlers/settings.py
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from sqlalchemy import update
from database.db import async_session
from database.models import User
from keyboards.inline import get_settings_buttons, get_voice_settings_buttons, get_daily_buttons, get_level_buttons
from utils.helpers import get_user_language, get_user_voice_settings, get_user_level, get_user_daily_settings

router = Router()


@router.message(F.text == "⚙️ Настройки")
async def show_settings_menu(message: Message):
    user_id = message.from_user.id
    lang = await get_user_language(user_id)
    level = await get_user_level(user_id)
    voice_q, voice_a = await get_user_voice_settings(user_id)
    q_day, t_day = await get_user_daily_settings(user_id)

    await message.answer(
        f"⚙️ Настройки:\n\n"
        f"Язык интерфейса: {lang}\n"
        f"Выбран уровень: {level}\n"
        f"Озвучка вопросов: {'включена' if voice_q else 'отключена'}\n"
        f"Озвучка ответов: {'включена' if voice_a else 'отключена'}\n"
        f"Вопрос дня: {'включен' if q_day else 'отключен'}\n"
        f"Совет дня: {'включен' if t_day else 'отключен'}",
        reply_markup=get_settings_buttons()
    )


@router.callback_query(F.data == "change_voice")
async def change_voice_menu(callback: CallbackQuery):
    await callback.message.edit_text("🔊 Озвучка", reply_markup=get_voice_settings_buttons())
    await callback.answer()


@router.callback_query(F.data.startswith("voice_"))
async def set_voice(callback: CallbackQuery):
    action, target = callback.data.split("_")[1:]
    user_id = callback.from_user.id

    async with async_session() as session:
        stmt = update(User).where(User.telegram_id == user_id)
        if target == "question":
            stmt = stmt.values(voice_enabled=(action == "on"))
        elif target == "answer":
            stmt = stmt.values(answer_enabled=(action == "on"))
        await session.execute(stmt)
        await session.commit()

    await callback.answer("Настройки озвучки обновлены ✅")
    await show_settings_menu(callback.message)


@router.callback_query(F.data == "daily_settings")
async def daily_settings_menu(callback: CallbackQuery):
    await callback.message.edit_text("📅 Настройки дня", reply_markup=get_daily_buttons())
    await callback.answer()


@router.callback_query(F.data.startswith("toggle_qotd"))
async def toggle_question_of_day(callback: CallbackQuery):
    user_id = callback.from_user.id
    async with async_session() as session:
        user = await session.get(User, user_id)
        user.question_of_the_day = not user.question_of_the_day
        await session.commit()
    await callback.answer("Изменено.")
    await daily_settings_menu(callback)


@router.callback_query(F.data.startswith("toggle_tip"))
async def toggle_tip_of_day(callback: CallbackQuery):
    user_id = callback.from_user.id
    async with async_session() as session:
        user = await session.get(User, user_id)
        user.tip_of_the_day = not user.tip_of_the_day
        await session.commit()
    await callback.answer("Изменено.")
    await daily_settings_menu(callback)


@router.callback_query(F.data == "change_level")
async def change_level_menu(callback: CallbackQuery):
    await callback.message.edit_text("📈 Выберите уровень сложности:", reply_markup=get_level_buttons())
    await callback.answer()


@router.callback_query(F.data.startswith("level_"))
async def set_level(callback: CallbackQuery):
    new_level = callback.data.split("_")[1]
    user_id = callback.from_user.id

    async with async_session() as session:
        stmt = update(User).where(User.telegram_id == user_id).values(level=new_level)
        await session.execute(stmt)
        await session.commit()

    await callback.answer("Уровень изменён ✅")
    await show_settings_menu(callback.message)
