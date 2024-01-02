from aiogram import F, Router, types
from aiogram.fsm.state import any_state
from aiogram.types import Message
from aiogram_dialog import DialogManager, StartMode

from src.api import client
from src.handlers.create_booking import CreateBookingStates
from src.handlers.my_bookings import _get_pretty_datetime, _create_inline_keyboard
from src.keyboards import registration, image_schedule_kb

router = Router()


@router.message(any_state, F.text == "Create a booking")
async def _start_booking(message: Message, dialog_manager: DialogManager):
    if not await client.is_user_exists(str(message.from_user.id)):
        await message.answer("Welcome! To continue, you need to register.", reply_markup=registration)
    else:
        await dialog_manager.start(CreateBookingStates.choose_date, mode=StartMode.NEW_STACK)


@router.message(any_state, F.text == "Show the image with bookings")
async def get_image_schedule(message: types.Message):
    if not await client.is_user_exists(str(message.from_user.id)):
        await message.answer("Welcome! To continue, you need to register.", reply_markup=registration)
    else:
        await message.answer(
            text="Do you want to see bookings for the current week or next one?",
            reply_markup=image_schedule_kb,
        )


@router.message(any_state, F.text == "My bookings")
async def show_my_bookings(message: Message):
    if not await client.is_user_exists(str(message.from_user.id)):
        await message.answer("Welcome! To continue, you need to register.", reply_markup=registration)
    else:
        telegram_id = message.from_user.id
        participant_id = await client.get_participant_id(telegram_id)
        bookings = await client.get_participant_bookings(participant_id)

        if not bookings:
            await message.answer("You don`t have active bookings.")
        else:
            bookings = [_get_pretty_datetime(entry) for entry in bookings]
            await message.answer("Your active bookings:", reply_markup=await _create_inline_keyboard(bookings))
