from aiogram import types, Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from keyboards.inline import language_menu
from keyboards.reply import main_menu_keyboard
from utils.helpers import get_user_language, get_welcome_text
from database.models import get_or_create_user

router = Router()

@router.message(CommandStart())
async def start_command(message: Message):
    user = await get_or_create_user(message.from_user)
    lang = get_user_language(user)
    
    # Приветственное сообщение
    welcome_text = get_welcome_text(lang)
    
    # Показываем выбор языка, если пользователь впервые
    if not user.language:
        await message.answer(
            welcome_text,
            reply_markup=language_menu()
        )
    else:
        await message.answer(
            welcome_text,
            reply_markup=main_menu_keyboard(lang)
        )
