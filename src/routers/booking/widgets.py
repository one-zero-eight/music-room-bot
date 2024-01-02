import datetime
from typing import List, Callable, Optional

from aiogram.types import InlineKeyboardButton, CallbackQuery
from aiogram_dialog import DialogManager, DialogProtocol
from aiogram_dialog.widgets.common import WhenCondition
from aiogram_dialog.widgets.kbd import Keyboard


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

    async def _render_keyboard(self, data: dict, manager: DialogManager) -> List[List[InlineKeyboardButton]]:
        # get chosen (only first and last) timeslots
        endpoint_timeslots = self.get_widget_data(manager, [])
        remaining_daily_hours = data.get("remaining_daily_hours", 2)
        available_timeslots = self.get_available_slots(endpoint_timeslots, remaining_daily_hours)

        # render keyboard
        keyboard = []

        for timeslot in self.timeslots:
            text = timeslot.strftime("%H:%M")
            callback_data = self._item_callback_data(timeslot.strftime("%H:%M"))

            if timeslot not in available_timeslots and timeslot not in endpoint_timeslots:
                text = " "
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
