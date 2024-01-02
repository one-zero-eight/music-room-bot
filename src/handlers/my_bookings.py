from datetime import datetime

from aiogram import Router, types, F

from src.api import client
from src.keyboards import MyBookingsCallbackData

router = Router()


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
    response = await client.delete_booking(booking_id)
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
