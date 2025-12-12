import asyncio
import logging
from aiogram import Bot, Dispatcher
from config import BOT_TOKEN
from database.mongo import check_connection
from bot.handlers import router as main_router

logging.basicConfig(level=logging.INFO)

async def main():
    # Проверка БД
    await check_connection()
    
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    
    dp.include_router(main_router)
    
    # Удаляем вебхуки и запускаем
    await bot.delete_webhook(drop_pending_updates=True)
    print("🚀 Skill Bot запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот остановлен")