# handlers/start.py
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from keyboards.reply import main_menu_keyboard
from services.access import register_user
from services.reminder import send_welcome_sequence

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message):
    await register_user(message.from_user)
    await message.answer(
        "👋 Добро пожаловать в LEVEL 4 Trainer!\n\n"
        "Этот бот поможет тебе подготовиться к устной части экзамена ICAO. "
        "Ты сможешь пройти обучение, тренироваться с вопросами, отрабатывать аварийные ситуации "
        "и даже пройти пробный экзамен.\n\n"
        "Рекомендуем начать с обучения, чтобы освоить структуру ответов и грамматику.",
        reply_markup=main_menu_keyboard(message.from_user.id)
    )
    await send_welcome_sequence(message.from_user.id)
# Start and setup handler
