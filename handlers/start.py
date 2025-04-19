from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from keyboards.reply import main_menu
from keyboards.inline import get_language_menu
from database.db import async_session
from database.models import User
from sqlalchemy.future import select

router = Router()

@router.message(F.text == "/start")
async def start_handler(message: Message):
    await message.answer(
        "👋 Добро пожаловать в LEVEL 4 Trainer!\n\n"
        "Этот бот поможет вам подготовиться к устной части экзамена ICAO.\n"
        "Давайте начнём с выбора языка интерфейса.",
        reply_markup=get_language_menu()
    )
    async with async_session() as session:
        result = await session.execute(select(User).where(User.user_id == message.from_user.id))
        user = result.scalar()
        if not user:
            new_user = User(
                user_id=message.from_user.id,
                full_name=message.from_user.full_name,
                username=message.from_user.username,
                language=message.from_user.language_code
            )
            session.add(new_user)
            await session.commit()
