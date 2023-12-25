import asyncio
import json
from datetime import date, datetime, time, timedelta

import aiohttp
from aiogram import F, Router
from aiogram.filters.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message
from aiogram_dialog import Dialog, DialogManager, StartMode, Window
from aiogram_dialog.widgets.kbd import Back, Button, Calendar, Group
from aiogram_dialog.widgets.text import Const
from aiohttp import ClientResponse

from src.handlers.registration import is_user_exists
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


async def get_user_id(telegram_id: int) -> str:
    url = "http://127.0.0.1:8000/participants/participant_id"
    params = {"telegram_id": telegram_id}
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as response:
            if response.status == 200:
                res = await response.text()
                return res


async def run_process_booking_creation(user_id: str, time_start: str, time_end: str) -> tuple[ClientResponse, json]:
    params = {
        "participant_id": user_id,
        "time_start": time_start,
        "time_end": time_end,
    }
    async with aiohttp.ClientSession() as session:
        url = "http://127.0.0.1:8000/bookings/"
        async with session.post(url, json=params) as response:
            response_text = await response.text()
            response_json = json.loads(response_text)
            return response, response_json


async def on_end_time_selected(callback: CallbackQuery, button: Button, manager: DialogManager):
    telegram_id = callback.from_user.id
    user_id = await get_user_id(telegram_id)
    date = str(manager.dialog_data.get("selected_date")).split("-")
    date = list(map(int, date))
    start_time = manager.dialog_data.get("selected_start_time")
    end_time = callback.data
    time_start = (str(datetime(*date, int(start_time[:2]), int(start_time[2:])))).replace(" ", "T")
    time_end = (str(datetime(*date, int(end_time[:2]), int(end_time[2:])))).replace(" ", "T")
    response, response_text = await run_process_booking_creation(user_id, time_start, time_end)
    if response.status == 200:
        await callback.message.answer(f"You have successfully booked on {date}: {start_time}-{callback.data}")
        await manager.done()
    else:
        await callback.message.answer(f"Error occurred: {response_text.get('detail')}")
        await manager.switch_to(CreateBookingProcedure.choose_date)


async def setup_available_slots():
    global start_time_group, end_time_group
    start_time_group = Group(
        *await start_time_button_generator(),
        width=4,
    )

    end_time_group = Group(
        *await end_time_button_generator(),
        width=4,
    )


@router.message(F.text == "Create a booking")
async def get_image_schedule(message: Message, dialog_manager: DialogManager):
    if not await is_user_exists(str(message.from_user.id)):
        await message.answer("Welcome! To continue, you need to register.", reply_markup=registration)
    else:
        await dialog_manager.start(CreateBookingProcedure.choose_date, mode=StartMode.RESET_STACK)
        await setup_available_slots()


async def get_daily_bookings():
    async with aiohttp.ClientSession() as session:
        url = "http://127.0.0.1:8000/bookings/daily_bookings"
        params = {"day": datetime.now().isoformat()}
        async with session.get(url, params=params) as response:
            response_text = await response.text()
            response_json = json.loads(response_text)
            return response, response_json


async def start_time_button_generator() -> list[Button]:
    available_slots = await get_available_start_slots("test")

    start_time = time(7, 0)

    time_buttons = []

    current_time = start_time
    for slot in available_slots:
        button_id = f"{slot.replace(':', '').replace(' ', '_')}"

        time_buttons.append(Button(Const(slot), id=button_id, on_click=on_start_time_selected))

        current_time = (datetime.combine(datetime.today(), current_time) + timedelta(minutes=30)).time()

    return time_buttons


async def get_available_end_slots(mode: str):
    response, response_text = await get_daily_bookings()

    booking_intervals = []

    for item in response_text:
        start_time = datetime.fromisoformat(item['time_start'])
        end_time = datetime.fromisoformat(item['time_end'])

        formatted_item = [start_time.strftime('%H:%M'), end_time.strftime('%H:%M')]
        booking_intervals.append(formatted_item)

    # Generate all time slots from 07:00 to 22:00
    all_time_slots = [f'{hour:02d}:{minute:02d}' for hour in range(7, 23) for minute in (0, 30)]

    # Remove booked intervals and intervals that start or end at booked times from available time slots
    available_time_slots = [slot for slot in all_time_slots if
                            not any(start <= slot < end or start <= slot <= end for start, end in booking_intervals)]

    return available_time_slots


async def get_available_start_slots(mode: str):
    response, response_text = await get_daily_bookings()

    booking_intervals = []

    for item in response_text:
        start_time = datetime.fromisoformat(item['time_start'])
        end_time = datetime.fromisoformat(item['time_end'])

        formatted_item = [start_time.strftime('%H:%M'), end_time.strftime('%H:%M')]

        booking_intervals.append(formatted_item)

    # Generate all time slots from 07:00 to 22:00
    all_time_slots = [f'{hour:02d}:{minute:02d}' for hour in range(7, 23) for minute in (0, 30)]

    # Remove booked intervals and intervals that start at booked times from available time slots
    available_time_slots = [slot for slot in all_time_slots if
                            not any(start <= slot < end for start, end in booking_intervals)]

    return available_time_slots


async def end_time_button_generator() -> list[Button]:
    available_slots = await get_available_end_slots("test")

    start_time = time(7, 0)
    time_buttons = []

    current_time = start_time
    for slot in available_slots:
        button_id = f"{slot.replace(':', '').replace(' ', '_')}"

        time_buttons.append(Button(Const(slot), id=button_id, on_click=on_end_time_selected))

        current_time = (datetime.combine(datetime.today(), current_time) + timedelta(minutes=30)).time()

    return time_buttons


date_selection = Window(
    Const("Please select a date:"),
    Calendar(id="calendar", on_click=on_date_selected),
    state=CreateBookingProcedure.choose_date,
)

start_time_group = Group(
    *asyncio.run(start_time_button_generator()),
    width=4,
)

end_time_group = Group(
    *asyncio.run(end_time_button_generator()),
    width=4,
)

start_time_selection = Window(
    Const("Please select start time:"),
    start_time_group,
    Back(),
    state=CreateBookingProcedure.choose_start_time,
)

end_time_selection = Window(
    Const("Please select end time:"),
    end_time_group,
    Back(),
    state=CreateBookingProcedure.choose_end_time,
)

dialog = Dialog(date_selection, start_time_selection, end_time_selection)

router.include_router(dialog)
