from datetime import datetime

from aiogram import types, F
from aiogram.filters import Command
from aiogram.fsm.state import any_state
from aiogram.types import Message

from src.api import client
from src.routers.booking import router
from src.routers.booking.callback_data import MyBookingsCallbackData


@router.message(any_state, Command("my_bookings"))
@router.message(any_state, F.text == "My bookings")
async def show_my_bookings(message: Message):
    bookings = await client.get_participant_bookings(message.from_user.id)

    if not bookings:
        await message.answer("You don't have active bookings.")
    else:
        bookings = [_get_pretty_datetime(entry) for entry in bookings]
        await message.answer("Your active bookings:", reply_markup=await _create_inline_keyboard(bookings))


async def _create_inline_keyboard(bookings: list[dict]):
    keyboard = [[]]

    for booking in bookings:
        button1_text = f"{booking['time_start']}-{booking['time_end'][-5:]}"
        button2_text = "❌"

        button1 = types.InlineKeyboardButton(
            text=button1_text, callback_data=MyBookingsCallbackData(id=booking["id"], key="none").pack()
        )
        button2 = types.InlineKeyboardButton(
            text=button2_text, callback_data=MyBookingsCallbackData(id=booking["id"], key="cancel").pack()
        )

        keyboard.append([button1, button2])

    return types.InlineKeyboardMarkup(inline_keyboard=keyboard)


@router.callback_query(MyBookingsCallbackData.filter(F.key == "cancel"))
async def handle_delete_callback(callback_query: types.CallbackQuery, callback_data: MyBookingsCallbackData):
    booking_id = callback_data.id
    response = await client.delete_booking(booking_id, callback_query.from_user.id)
    if response:
        await callback_query.answer(text="You have successfully cancel the booking")
    else:
        await callback_query.answer(text="No such booking found")


@router.callback_query(MyBookingsCallbackData.filter(F.key == "none"))
async def handle_none_callback(callback_query: types.CallbackQuery):
    await callback_query.answer()


def _get_pretty_datetime(data):
    for key in ["time_start", "time_end"]:
        date_object = datetime.strptime(data[key], "%Y-%m-%dT%H:%M:%S")
        data[key] = date_object.strftime("%b %d %H:%M")
    return data
