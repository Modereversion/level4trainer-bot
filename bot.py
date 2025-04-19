import logging
from aiogram import Bot, Dispatcher
from aiogram.utils import executor
import os
from config import BOT_TOKEN
from handlers import (
    start, learning, training, emergencies,
    exam, settings, admin
)
from services import reminder

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

# Регистрируем хендлеры
start.register_handlers(dp)
learning.register_handlers(dp)
training.register_handlers(dp)
emergencies.register_handlers(dp)
exam.register_handlers(dp)
settings.register_handlers(dp)
admin.register_handlers(dp)

async def on_startup(dp):
    # Инициализация БД, CRON-напоминаний и т.д.
    await reminder.setup(dp)
    logging.info("Бот запущен!")

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
