from datetime import date, datetime, time, timedelta

import aiohttp
from aiogram import F, Router
from aiogram.filters import Command
from aiogram.filters.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message
from aiogram_dialog import Dialog, DialogManager, StartMode, Window
from aiogram_dialog.widgets.kbd import Button, Calendar, Group
from aiogram_dialog.widgets.text import Const

from src.handlers.registration import is_user_exists, start
from src.keyboards import registration

router = Router()


class CreateBookingProcedure(StatesGroup):
    choose_date = State()
    choose_start_time = State()
    choose_end_time = State()


async def on_date_selected(callback: CallbackQuery, widget, manager: DialogManager, selected_date: date):
    manager.dialog_data["selected_date"] = selected_date
    await manager.next()


async def on_start_time_selected(callback: CallbackQuery, button: Button, manager: DialogManager):
    manager.dialog_data["selected_start_time"] = callback.data
    await manager.next()


async def get_user_id(telegram_id: str) -> str:
    ...


async def on_end_time_selected(callback: CallbackQuery, button: Button, manager: DialogManager):
    # TODO Получить user_id на основе telegram_id
    telegram_id = str(callback.message.from_user.id)
    user_id = await get_user_id(telegram_id)
    date = manager.dialog_data.get("selected_date")
    date = str(date).split("-")
    date = list(map(int, date))
    start_time = manager.dialog_data.get("selected_start_time")
    end_time = callback.data
    time_start = datetime(*date, int(start_time[:2]), int(start_time[2:]))
    time_end = datetime(*date, int(end_time[:2]), int(end_time[2:]))
    params = {
        "participant_id": str(1),
        "time_start": str(time_start),
        "time_end": str(time_end),
    }
    async with (aiohttp.ClientSession() as session):
        url = "http://127.0.0.1:8000/bookings/create_booking"
        async with session.post(url, json=params) as response:
            if response.status == 200:
                await callback.message.answer(f"You have successfully booked on {date}: {start_time}-{callback.data}")
            else:
                await callback.message.answer("Error in creating booking.")

    await manager.done()


@router.message(F.text == "Create a booking")
async def get_image_schedule(message: Message, dialog_manager: DialogManager):
    if not await is_user_exists(str(message.from_user.id)):
        await message.answer("Welcome! To continue, you need to register.", reply_markup=registration)
    else:
        # Important: always set `mode=StartMode.RESET_STACK` you don't want to stack dialogs
        await dialog_manager.start(CreateBookingProcedure.choose_date, mode=StartMode.RESET_STACK)


def start_time_button_generator() -> list[Button]:
    start_time = time(7, 0)
    end_time = time(22, 0)

    # Create a list to store the button widgets
    time_buttons = []

    # Generate buttons with 30-minute intervals
    current_time = start_time
    while current_time <= end_time:
        # Convert the current time to a string for button label in 24-hour format
        time_option = current_time.strftime("%H:%M")

        # Generate a valid button ID
        button_id = f"{time_option.replace(':', '').replace(' ', '_')}"

        # Create the button and add it to the list
        time_buttons.append(Button(Const(time_option), id=button_id, on_click=on_start_time_selected))

        # Increment the current time by 30 minutes
        current_time = (datetime.combine(datetime.today(), current_time) + timedelta(minutes=30)).time()

    return time_buttons


def end_time_button_generator(status: str) -> list[Button]:
    start_time = time(7, 0)
    end_time = time(22, 0)
    # Create a list to store the button widgets
    time_buttons = []

    # Generate buttons with 30-minute intervals
    current_time = start_time
    while current_time <= end_time:
        # Convert the current time to a string for button label in 24-hour format
        time_option = current_time.strftime("%H:%M")

        # Generate a valid button ID
        button_id = f"{time_option.replace(':', '').replace(' ', '_')}"

        # Create the button and add it to the list
        time_buttons.append(Button(Const(time_option), id=button_id, on_click=on_end_time_selected))

        # Increment the current time by 30 minutes
        current_time = (datetime.combine(datetime.today(), current_time) + timedelta(minutes=30)).time()

    return time_buttons


date_selection = Window(
    Const("Please select a date:"),
    Calendar(id="calendar", on_click=on_date_selected),
    state=CreateBookingProcedure.choose_date,
)

start_time_group = Group(
    *start_time_button_generator(),
    width=4,
)

end_time_group = Group(
    *end_time_button_generator("free"),
    width=4,
)

start_time_selection = Window(
    Const("Please select start time:"), start_time_group, state=CreateBookingProcedure.choose_start_time
)

end_time_selection = Window(
    Const("Please select end time:"), end_time_group, state=CreateBookingProcedure.choose_end_time
)

dialog = Dialog(date_selection, start_time_selection, end_time_selection)

router.include_router(dialog)
