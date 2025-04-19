import asyncio
from aiogram import Bot, Dispatcher
from aiogram.enums.parse_mode import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand
from config import load_config
from database.db import init_db
from handlers import start, training, learning, exam, emergencies, settings, admin

async def main():
    config = load_config()
    bot = Bot(token=config.bot_token, parse_mode=ParseMode.HTML)
    dp = Dispatcher(storage=MemoryStorage())

    # Инициализация базы данных
    await init_db(config.database_url)

    # Регистрация всех обработчиков
    for router in [
        start.router,
        training.router,
        learning.router,
        exam.router,
        emergencies.router,
        settings.router,
        admin.router,
    ]:
        dp.include_router(router)

    # Команды бота
    await bot.set_my_commands([
        BotCommand(command="start", description="Начать"),
    ])

    # Запуск бота
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
