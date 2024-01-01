import json
from datetime import datetime

import aiohttp
from aiogram import Router, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

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


async def create_inline_keyboard(n: int, bookings: list[dict]):
    keyboard = [[]]

    for i in range(n):
        button1 = InlineKeyboardButton(text=f"{bookings[i]['time_start']} - {bookings[i]['time_end'][-5:]}",
                                       callback_data=f'action_{2 * i + 1}')
        button2 = InlineKeyboardButton(text='Удалить', callback_data=f'delete_booking_{i}')

        keyboard += [[button1, button2]]

    return InlineKeyboardMarkup(inline_keyboard=keyboard, row_width=2)


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

        if not len(response_json):
            await message.answer("You don`t have active bookings.")
        else:
            bookings = [get_pretty_datetime(entry) for entry in response_json]
            await message.answer("Inline buttons:", reply_markup=await create_inline_keyboard(len(bookings), bookings))


def get_pretty_datetime(data):
    for key in ['time_start', 'time_end']:
        date_object = datetime.strptime(data[key], "%Y-%m-%dT%H:%M:%S")
        data[key] = date_object.strftime("%B %d %H:%M")
    return data
