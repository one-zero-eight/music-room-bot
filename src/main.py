import asyncio
import logging
import os

from aiogram import Bot, Dispatcher
from aiogram.enums.parse_mode import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import find_dotenv, load_dotenv

from src.handlers import routers

load_dotenv(find_dotenv())

bot = Bot(token=os.getenv("TOKEN"), parse_mode=ParseMode.HTML)


async def main():
    dp = Dispatcher(storage=MemoryStorage())
    for router in routers:
        dp.include_router(router)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
