# bot.py
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.strategy import FSMStrategy
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.bot import DefaultBotProperties

from config import BOT_TOKEN
from handlers import start, training, learning, exam, emergencies, settings, admin
from database.db import create_db


async def main():
    await create_db()

    dp = Dispatcher(storage=MemoryStorage(), fsm_strategy=FSMStrategy.CHAT)
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    dp.include_routers(
        start.router,
        training.router,
        learning.router,
        exam.router,
        emergencies.router,
        settings.router,
        admin.router
    )

    print("Bot started...")
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
