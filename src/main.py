import asyncio
import logging
import os

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram_dialog import setup_dialogs
from dotenv import find_dotenv, load_dotenv

from src.handlers import routers

load_dotenv(find_dotenv())

bot = Bot(token=os.getenv("TOKEN"))


async def main():
    dp = Dispatcher(storage=MemoryStorage())
    for router in routers:
        dp.include_router(router)
    setup_dialogs(dp)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
