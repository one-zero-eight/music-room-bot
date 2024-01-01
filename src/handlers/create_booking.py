import datetime
from typing import Optional, List, Callable

from aiogram import F, Router
from aiogram.filters.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message, InlineKeyboardButton, User
from aiogram_dialog import Dialog, DialogManager, StartMode, Window, DialogProtocol
from aiogram_dialog.widgets.common import WhenCondition
from aiogram_dialog.widgets.kbd import Back, Button, Calendar, Keyboard, Group
from aiogram_dialog.widgets.text import Const

from src.api import client
from src.keyboards import registration

router = Router()


class CreateBookingProcedure(StatesGroup):
    choose_date = State()
    choose_time = State()


async def on_date_selected(
    callback: CallbackQuery,
    widget,
    manager: DialogManager,
    selected_date: datetime.date,
):
    manager.dialog_data["selected_date"] = selected_date
    await manager.next()


async def on_time_confirmed(callback: CallbackQuery, button: Button, manager: DialogManager):
    telegram_id = callback.from_user.id
    user_id = await client.get_participant_id(telegram_id)
    date: datetime.date = manager.dialog_data.get("selected_date")

    chosen_timeslots = time_selection_widget.get_endpoint_timeslots(manager)

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
        await manager.done()
    else:
        await callback.message.answer(f"Error occurred: {error}")
        await manager.switch_to(CreateBookingProcedure.choose_date)


@router.message(F.text == "Create a booking")
async def _start_booking(message: Message, dialog_manager: DialogManager):
    if not await client.is_user_exists(str(message.from_user.id)):
        await message.answer("Welcome! To continue, you need to register.", reply_markup=registration)
    else:
        await dialog_manager.start(CreateBookingProcedure.choose_date, mode=StartMode.RESET_STACK)


class TimeRangeWidget(Keyboard):
    """
    Widget for time selection: 07:00, 07:30, 08:00, ...
    """

    def get_available_slots(self, chosen: list[datetime.time], hours: float) -> list[datetime.time]:
        """
        Get available timeslots
        :param chosen: list of chosen timeslots
        :param max_count: max number of chosen timeslots
        :return: list of available timeslots
        """
        if len(chosen) == 0:
            return self.timeslots
        elif len(chosen) == 1:
            start = chosen[0]
            index_of_start = self.timeslots.index(chosen[0])

            available_slots = []
            for timeslot in self.timeslots[index_of_start + 1:]:
                if timeslot.hour - start.hour >= hours:
                    break
                available_slots.append(timeslot)
            return available_slots
        return []

    async def _render_keyboard(self, data: dict, manager: DialogManager) -> List[List[InlineKeyboardButton]]:
        # get chosen (only first and last) timeslots
        endpoint_timeslots = self.get_widget_data(manager, [])
        remaining_daily_hours = int(data.get("remaining_daily_hours", 2))
        available_timeslots = self.get_available_slots(endpoint_timeslots, remaining_daily_hours)

        # render keyboard
        keyboard = []

        for timeslot in self.timeslots:
            text = timeslot.strftime("%H:%M")
            callback_data = self._item_callback_data(timeslot.strftime("%H:%M"))

            if timeslot not in available_timeslots and timeslot not in endpoint_timeslots:
                text = "."
                callback_data = self._item_callback_data("None")

            if endpoint_timeslots and timeslot == endpoint_timeslots[0]:
                text = f"{text} -"
            if endpoint_timeslots and timeslot == endpoint_timeslots[-1]:
                text = f"- {text}"

            keyboard.append(
                [
                    InlineKeyboardButton(
                        text=text,
                        callback_data=callback_data,
                    )
                ]
            )

        return keyboard

    async def _process_item_callback(
        self,
        callback: CallbackQuery,
        data: str,
        dialog: DialogProtocol,
        manager: DialogManager,
    ) -> bool:
        """
        Process callback from item
        :param callback: callback
        :param data: callback data
        :param dialog: dialog
        :param manager: dialog manager
        :return: True if processed
        """
        if data == "None":
            return False

        clicked_timeslot = datetime.time.fromisoformat(data)

        if clicked_timeslot in self.timeslots:
            # add or remove timeslot
            endpoint_timeslots = self.get_widget_data(manager, [])
            if clicked_timeslot in endpoint_timeslots:
                endpoint_timeslots.remove(clicked_timeslot)
            else:
                endpoint_timeslots.append(clicked_timeslot)
            self.set_widget_data(manager, endpoint_timeslots)
            return True
        return False

    def get_endpoint_timeslots(self, manager: DialogManager) -> list[datetime.time]:
        """
        Get endpoint timeslots
        :param manager: dialog manager
        :return: list of timeslots
        """
        return self.get_widget_data(manager, [])

    def __init__(
        self,
        timeslots: list[datetime.time] | Callable[..., list[datetime.time]],
        id: Optional[str] = None,
        when: WhenCondition = None,
    ):
        super().__init__(id=id, when=when)
        self._timeslots = timeslots

    @property
    def timeslots(self) -> list[datetime.time]:
        """
        Get timeslots
        :return: list of timeslots
        """
        if callable(self._timeslots):
            return self._timeslots()
        return self._timeslots


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
    state=CreateBookingProcedure.choose_date,
)

time_selection_widget = TimeRangeWidget(
    timeslots=generate_timeslots(datetime.time(7, 0), datetime.time(22, 30), 30),
    id="time_selection",
)


async def getter_for_time_selection(dialog_manager: DialogManager, **kwargs) -> dict:
    dialog_data: dict = dialog_manager.dialog_data
    event_from_user: User = kwargs.get("event_from_user")
    date: datetime.date = dialog_data.get("selected_date")
    if date is None:
        return {}
    participant_id = await client.get_participant_id(event_from_user.id)
    remaining_daily_hours = await client.get_remaining_daily_hours(participant_id, date)
    return {"remaining_daily_hours": remaining_daily_hours}


time_selection = Window(
    Const("Please select start time:"),
    Group(time_selection_widget, width=4),
    Back(),
    Button(Const("Done"), id="done", on_click=on_time_confirmed),
    getter=getter_for_time_selection,
    state=CreateBookingProcedure.choose_time,
)

dialog = Dialog(date_selection, time_selection)

router.include_router(dialog)
