import datetime
from typing import Any

from aiogram import F
from aiogram.fsm.state import any_state
from aiogram.types import CallbackQuery, Message
from aiogram_dialog import Dialog, DialogManager, Window, StartMode
from aiogram_dialog.widgets.kbd import Back, Button, Calendar, Group, Cancel, Row
from aiogram_dialog.widgets.text import Const, Format

from src.api import client
from src.routers.booking import router
from src.routers.booking.states import CreateBookingStates
from src.routers.booking.widgets import TimeRangeWidget


@router.message(any_state, F.text == "Create a booking")
async def start_booking(_message: Message, dialog_manager: DialogManager, api_user_id: int):
    await dialog_manager.start(
        CreateBookingStates.choose_date, mode=StartMode.NEW_STACK, data={"api_user_id": api_user_id}
    )


async def on_date_selected(
    _callback: CallbackQuery, _widget, dialog_manager: DialogManager, selected_date: datetime.date
):
    dialog_manager.dialog_data["selected_date"] = selected_date
    await dialog_manager.next()


async def on_time_confirmed(callback: CallbackQuery, _button: Button, dialog_manager: DialogManager):
    user_id = dialog_manager.start_data["api_user_id"]
    date: datetime.date = dialog_manager.dialog_data["selected_date"]

    chosen_timeslots = time_selection_widget.get_endpoint_timeslots(dialog_manager)

    if len(chosen_timeslots) != 2:
        await callback.message.answer("You must choose both start and end time")
        return
    start, end = chosen_timeslots

    success, error = await client.book(user_id, date, start, end)

    if success:
        date_text = date.strftime("%B %d")
        timeslot_text = f"{start.isoformat(timespec='minutes')} - {end.isoformat(timespec='minutes')}"
        text = f"You have successfully booked on <b>{date_text}, {timeslot_text}</b>"
        await callback.message.answer(text, parse_mode="HTML")
        await dialog_manager.done()
    else:
        await callback.message.answer(f"Error occurred: {error}")
        await dialog_manager.switch_to(CreateBookingStates.choose_date)


def generate_timeslots(start_time: datetime.time, end_time: datetime.time, interval: int) -> list[datetime.time]:
    """
    Generate timeslots from start_time to end_time with interval
    :param start_time: start time
    :param end_time: end time
    :param interval: interval in minutes
    :return: list of timeslots
    """
    timeslots = []
    current_time = start_time
    while current_time <= end_time:
        timeslots.append(current_time)
        current_time = (
            datetime.datetime.combine(datetime.datetime.today(), current_time) + datetime.timedelta(minutes=interval)
        ).time()
    return timeslots


date_selection = Window(
    Const("Please select a date:"),
    Calendar(id="calendar", on_click=on_date_selected),
    Cancel(Const("❌")),
    state=CreateBookingStates.choose_date,
)

time_selection_widget = TimeRangeWidget(
    timeslots=generate_timeslots(datetime.time(7, 0), datetime.time(22, 30), 30),
    id="time_selection",
)


async def getter_for_time_selection(dialog_manager: DialogManager, **_kwargs) -> dict:
    dialog_data: dict = dialog_manager.dialog_data
    participant_id = dialog_manager.start_data["api_user_id"]
    date: datetime.date = dialog_data["selected_date"]
    data: dict[str, Any] = {"selected_date": date, "participant_id": participant_id}
    hours = await client.get_remaining_daily_hours(participant_id, date)
    data["remaining_daily_hours"] = hours
    data["remaining_daily_hours_hours"] = int(hours)
    data["remaining_daily_hours_minutes"] = int((hours - data["remaining_daily_hours_hours"]) * 60)
    data["daily_bookings"] = await client.get_daily_bookings(date)
    return data


time_selection = Window(
    Format(
        "Please select a time slot for <b>{dialog_data[selected_date]}</b>.\n"
        "You have <b>{remaining_daily_hours_hours:0.0f}h {remaining_daily_hours_minutes:0.0f}m</b> free.",
    ),
    Group(time_selection_widget, width=4),
    Row(
        Back(Const("🔙")),
        Button(Const("✅"), id="done", on_click=on_time_confirmed),
    ),
    getter=getter_for_time_selection,
    state=CreateBookingStates.choose_time,
    parse_mode="HTML",
)

dialog = Dialog(date_selection, time_selection)

router.include_router(dialog)
