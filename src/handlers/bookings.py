import json

import aiohttp
from aiogram import Router, F
from aiogram.types import Message

from src.handlers.registration import is_user_exists
from src.keyboards import registration

router = Router()


async def get_participant_id(telegram_id: int):
    url = "http://127.0.0.1:8000/participants/participant_id"
    params = {"telegram_id": str(telegram_id)}
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as response:
            response_text = await response.text()
            response_json = json.loads(response_text)
            return response_json


@router.message(F.text == "My bookings")
async def show_my_bookings(message: Message):
    if not await is_user_exists(str(message.from_user.id)):
        await message.answer("Welcome! To continue, you need to register.", reply_markup=registration)
    else:
        telegram_id = message.from_user.id
        participant_id = await get_participant_id(telegram_id)
        url = f"http://127.0.0.1:8000/bookings/{participant_id}"
        params = {"participant_id": str(participant_id)}

        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                response_text = await response.text()
                response_json = json.loads(response_text)
                print(response_json)

        msg = ''

        for booking in response_json:
            msg += booking['time_start'] + " " + booking['time_end'] + "\n"

        await message.answer(msg)
