from aiogram import executor
from loader import dp
from handlers import start, learning, training, emergencies, exam, settings, admin
from database.db import init_db

async def on_startup(dp):
    # Инициализация БД
    await init_db()

# Регистрируем все хендлеры
start.register_handlers(dp)
learning.register_handlers(dp)
training.register_handlers(dp)
emergencies.register_handlers(dp)
exam.register_handlers(dp)
settings.register_handlers(dp)
admin.register_handlers(dp)

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
