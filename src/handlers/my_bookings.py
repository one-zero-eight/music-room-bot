from datetime import datetime

from aiogram import Router, F, types
from aiogram.types import Message

from src.api import client
from src.keyboards import registration

router = Router()


async def _create_inline_keyboard(bookings: list[dict]):
    keyboard = [[]]

    for booking in bookings:
        button1_text = f"{booking['time_start']} - {booking['time_end'][-5:]}"
        button2_text = 'Cancel'

        button1 = types.InlineKeyboardButton(text=button1_text, callback_data='plug')
        button2 = types.InlineKeyboardButton(text=button2_text, callback_data=f'cancel_{booking["id"]}')

        keyboard += [[button1, button2]]

    return types.InlineKeyboardMarkup(inline_keyboard=keyboard, row_width=2)


@router.callback_query(lambda c: c.data.startswith('cancel'))
async def handle_delete_callback(callback_query: types.CallbackQuery):
    booking_id = int(callback_query.data.split('_')[1])

    response = await client.delete_booking(booking_id)
    if response:
        await callback_query.answer(text="You have successfully cancel the booking", show_alert=True)
    else:
        await callback_query.answer(text="No such booking found", show_alert=True)


@router.message(F.text == "My bookings")
async def show_my_bookings(message: Message):
    if not await client.is_user_exists(str(message.from_user.id)):
        await message.answer("Welcome! To continue, you need to register.", reply_markup=registration)
    else:
        telegram_id = message.from_user.id
        participant_id = await client.get_participant_id(telegram_id)

        bookings = await client.get_participant_bookings(participant_id)

        if not len(bookings):
            await message.answer("You don`t have active bookings.")
        else:
            bookings = [_get_pretty_datetime(entry) for entry in bookings]
            await message.answer("Your active bookings:",
                                 reply_markup=await _create_inline_keyboard(bookings))


def _get_pretty_datetime(data):
    for key in ['time_start', 'time_end']:
        date_object = datetime.strptime(data[key], "%Y-%m-%dT%H:%M:%S")
        data[key] = date_object.strftime("%b %d %H:%M")
    return data
