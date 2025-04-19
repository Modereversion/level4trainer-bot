import asyncio
from aiogram import Bot, Dispatcher
from config import settings
from database.db import init_db
from handlers import start, training, learning, exam, emergencies, settings as user_settings, admin
from keyboards.reply import main_menu

bot = Bot(token=settings.BOT_TOKEN, parse_mode='HTML')
dp = Dispatcher()

dp.include_routers(
    start.router,
    training.router,
    learning.router,
    exam.router,
    emergencies.router,
    user_settings.router,
    admin.router
)

async def main():
    await init_db()
    await bot.delete_webhook(drop_pending_updates=True)
    await bot.set_my_commands([], scope=None)
    await bot.set_chat_menu_button(menu_button=main_menu)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
