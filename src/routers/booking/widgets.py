import datetime
from typing import List, Callable, Optional, TypedDict

from aiogram.types import InlineKeyboardButton, CallbackQuery
from aiogram_dialog import DialogManager, DialogProtocol
from aiogram_dialog.widgets.common import WhenCondition
from aiogram_dialog.widgets.kbd import Keyboard


class Booking(TypedDict):
    id: int
    participant_id: int
    participant_alias: str
    time_start: str
    time_end: str


class TimeRangeWidget(Keyboard):
    """
    Widget for time selection: 07:00, 07:30, 08:00, ...
    """

    def reset(self, manager: DialogManager):
        """
        Reset widget data
        :param manager: dialog manager
        """
        self.set_widget_data(manager, [])

    def get_available_slots(self, chosen: list[datetime.time], hours: float) -> list[datetime.time]:
        """
        Get available timeslots
        :param chosen: list of chosen timeslots
        :param max_count: max number of chosen timeslots
        :return: list of available timeslots
        """

        if hours <= 0:
            return []
        if len(chosen) == 0:
            return self.timeslots
        elif len(chosen) == 1:
            start = chosen[0]
            index_of_start = self.timeslots.index(chosen[0])
            _date_for_compare = datetime.date.today()
            available_slots = []
            for timeslot in self.timeslots[index_of_start + 1 :]:
                diff = datetime.datetime.combine(_date_for_compare, timeslot) - datetime.datetime.combine(
                    _date_for_compare, start
                )
                if diff.total_seconds() / 3600 > hours:
                    break
                available_slots.append(timeslot)
            return available_slots
        return []

    def get_already_booked_timeslots(self, daily_bookings: list[Booking]) -> dict[datetime.time, Booking]:
        """
        Get already booked timeslots
        :param daily_bookings: list of daily bookings
        :return: list of already booked timeslots
        """
        already_booked_timeslots: dict[datetime.time, Booking] = {}
        for timeslot in self.timeslots:
            for booking in daily_bookings:
                time_start = datetime.datetime.fromisoformat(booking["time_start"])
                time_end = datetime.datetime.fromisoformat(booking["time_end"])

                if time_start.time() <= timeslot <= time_end.time():
                    already_booked_timeslots[timeslot] = booking
                    break
        return already_booked_timeslots

    async def _render_keyboard(self, data: dict, manager: DialogManager) -> List[List[InlineKeyboardButton]]:
        # get chosen (only first and last) timeslots
        endpoint_timeslots = self.get_widget_data(manager, [])
        remaining_daily_hours = data["remaining_daily_hours"]
        available_timeslots = self.get_available_slots(endpoint_timeslots, remaining_daily_hours)
        daily_bookings: list[Booking] = data["daily_bookings"]
        already_booked_timeslots = self.get_already_booked_timeslots(daily_bookings)
        interactive_timeslots = set(available_timeslots) | set(endpoint_timeslots)
        for timeslot in already_booked_timeslots:
            if timeslot in interactive_timeslots:
                interactive_timeslots.remove(timeslot)
        # render keyboard
        keyboard = []

        for timeslot in self.timeslots:
            time_text = timeslot.strftime("%H:%M")

            if timeslot in interactive_timeslots:
                if endpoint_timeslots and timeslot == endpoint_timeslots[0]:
                    text = f"{time_text} -"
                elif endpoint_timeslots and timeslot == endpoint_timeslots[-1]:
                    text = f"- {time_text}"
                else:
                    text = time_text
                button = InlineKeyboardButton(
                    text=text,
                    callback_data=self._item_callback_data(time_text),
                )

            else:
                if timeslot in already_booked_timeslots:
                    booking = already_booked_timeslots[timeslot]
                    booked_by_id = booking["participant_id"]
                    booked_by_alias = booking["participant_alias"]
                    if booked_by_id == manager.start_data["api_user_id"]:
                        button = InlineKeyboardButton(text="🟢", callback_data=self._item_callback_data("None"))
                    else:
                        button = InlineKeyboardButton(text="🔴", url=f"https://t.me/{booked_by_alias}")
                else:
                    button = InlineKeyboardButton(text=" ", callback_data=self._item_callback_data("None"))

            keyboard.append([button])
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
            widget_data = self.get_widget_data(manager, [])
            if widget_data:
                self.set_widget_data(manager, [])
                return True

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
