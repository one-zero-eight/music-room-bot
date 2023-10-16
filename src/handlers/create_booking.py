from datetime import date

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.filters.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message
from aiogram_dialog import Dialog, DialogManager, StartMode, Window
from aiogram_dialog.widgets.kbd import Button, Calendar
from aiogram_dialog.widgets.text import Const

router = Router()


class CreateBookingProcedure(StatesGroup):
    choose_date = State()
    choose_start_time = State()
    choose_end_time = State()


async def on_date_selected(callback: CallbackQuery, widget, manager: DialogManager, selected_date: date):
    await callback.answer(f"Selected date: {selected_date}")
    await manager.next()


@router.message(F.text == "Create a booking")
async def get_image_schedule(message: Message, dialog_manager: DialogManager):
    # Important: always set `mode=StartMode.RESET_STACK` you don't want to stack dialogs
    await dialog_manager.start(CreateBookingProcedure.choose_date, mode=StartMode.RESET_STACK)


date_selection = Window(
    Const("Please select a date:"),
    Calendar(id="calendar", on_click=on_date_selected),

    state=CreateBookingProcedure.choose_date,
)

time_options = [
    "09:00 AM", "09:30 AM", "10:00 AM", "10:30 AM", "11:00 AM",
    "11:30 AM", "12:00 PM", "12:30 PM", "01:00 PM", "01:30 PM",
    "02:00 PM", "02:30 PM", "03:00 PM", "03:30 PM", "04:00 PM",
    "04:30 PM", "05:00 PM", "05:30 PM", "06:00 PM", "06:30 PM"
]

# Create an empty list to store the button widgets
time_button_ids = [f"time_{time_option.replace(':', '').replace(' ', '_')}" for time_option in time_options]

# Create a list of button widgets with valid IDs
time_buttons = [Button(Const(time_option), id=button_id) for time_option, button_id in
                zip(time_options, time_button_ids)]
time_selection = Window(
    Const("Please select a time:"),
    *time_buttons,
    state=CreateBookingProcedure.choose_start_time,
)

dialog = Dialog(date_selection, time_selection)

router.include_router(dialog)
