import asyncio
import logging

from aiogram import Bot, Dispatcher
from config import TOKEN
from app.handlers import router
from app.handlers import on_startup, on_shutdown

    
bot = Bot(token=TOKEN)
dp = Dispatcher()

async def main():
    logging.info("Starting bot...")

    await on_startup()

    dp.include_router(router)

    try:
        await dp.start_polling(bot)
    finally:
        await on_shutdown()

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Bot stopped by user")
