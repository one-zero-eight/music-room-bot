import asyncio
import logging
import os

from aiogram import Bot, Dispatcher
from aiogram import types
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram_dialog import setup_dialogs
from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())

bot = Bot(token=os.getenv("TOKEN"))
dp = Dispatcher(storage=MemoryStorage())


@dp.message(Command("start"))
async def start(message: types.Message):
    from src.api import client

    telegram_id = str(message.from_user.id)
    res = await client.is_user_exists(telegram_id)
    if res:
        from src.menu import menu_kb

        await message.answer("Welcome! Choose the action you're interested in.", reply_markup=menu_kb)
    else:
        from src.routers.registration.keyboards import registration_kb

        await message.answer("Welcome! To continue, you need to register.", reply_markup=registration_kb)


async def main():
    from src.routers import routers

    for router in routers:
        dp.include_router(router)
    setup_dialogs(dp)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
