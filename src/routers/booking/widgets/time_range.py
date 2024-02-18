import datetime
from typing import List, Callable, Optional, TypedDict, assert_never

from aiogram.types import InlineKeyboardButton, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
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
        self.set_widget_data(manager, [])

    def get_all_time_points(self) -> list[datetime.time]:
        return self.timepoints

    def get_end_time_points(self, start_time: datetime.time, hours: float) -> list[datetime.time]:
        if hours <= 0:
            return []

        timepoints = self.get_all_time_points()
        start_index = timepoints.index(start_time)
        _date = datetime.datetime.now().date()
        start_datetime = datetime.datetime.combine(_date, start_time)
        until_excluding = len(timepoints)

        for i in range(start_index, len(timepoints)):
            diff = datetime.datetime.combine(_date, timepoints[i]) - start_datetime
            if diff.total_seconds() / 3600 > hours:
                until_excluding = i
                break

        return timepoints[start_index:until_excluding]

    def get_already_booked_timepoints(
        self, daily_bookings: list[Booking], reverse: bool = False
    ) -> dict[datetime.time, Booking]:
        already_booked_timepoints: dict[datetime.time, Booking] = {}
        for timeslot in self.timepoints:
            for booking in daily_bookings:
                time_start = datetime.datetime.fromisoformat(booking["time_start"])
                time_end = datetime.datetime.fromisoformat(booking["time_end"])

                if not reverse and time_start.time() <= timeslot < time_end.time():
                    already_booked_timepoints[timeslot] = booking
                    break
                if reverse and time_start.time() < timeslot <= time_end.time():
                    already_booked_timepoints[timeslot] = booking
                    break
        return already_booked_timepoints

    def get_blocked_timepoints(
        self, selected_time: datetime.time | None, daily_bookings: list[Booking]
    ) -> list[datetime.time]:
        blocked_timepoints = []

        for i, timepoint in enumerate(self.timepoints):
            for booking in daily_bookings:
                booking_start_time = datetime.datetime.fromisoformat(booking["time_start"]).time()
                booking_end_time = datetime.datetime.fromisoformat(booking["time_end"]).time()
                if selected_time is None:
                    if booking_start_time <= timepoint < booking_end_time:
                        blocked_timepoints.append(timepoint)
                        break
                elif not (
                    (booking_start_time < selected_time and booking_end_time <= selected_time)
                    or (booking_start_time >= timepoint and booking_end_time > timepoint)
                ):
                    blocked_timepoints.append(timepoint)
                    break

        return blocked_timepoints

    async def _render_keyboard(self, data: dict, manager: DialogManager) -> List[List[InlineKeyboardButton]]:
        # get chosen (only first and last) timeslots
        endpoint_time_selected = self.get_selected_time_points(manager)
        remaining_daily_hours = data["remaining_daily_hours"]
        daily_bookings: list[Booking] = data["daily_bookings"]

        if len(endpoint_time_selected) == 0:
            # first click (select start time of booking)
            already_booked_timepoints = self.get_already_booked_timepoints(daily_bookings)
            available_timepoints_to_select = self.get_all_time_points() if remaining_daily_hours else []
            blocked_timepoints = self.get_blocked_timepoints(None, daily_bookings)
        elif len(endpoint_time_selected) == 1:
            # second click (select end time of booking)
            start_time = endpoint_time_selected[0]
            already_booked_timepoints = self.get_already_booked_timepoints(daily_bookings, reverse=True)
            available_timepoints_to_select = self.get_end_time_points(start_time, remaining_daily_hours)
            blocked_timepoints = self.get_blocked_timepoints(start_time, daily_bookings)
        elif len(endpoint_time_selected) == 2:
            # third click (remove end time of booking)
            already_booked_timepoints = self.get_already_booked_timepoints(daily_bookings, reverse=True)
            available_timepoints_to_select = []
            blocked_timepoints = []
        else:
            assert_never(endpoint_time_selected)

        # render keyboard
        keyboard_builer = InlineKeyboardBuilder()

        selected_date_string: str = manager.dialog_data["selected_date"]
        selected_date = datetime.datetime.strptime(selected_date_string, "%Y-%m-%d").date()
        timeslots = self.timepoints

        # do not show past timeslots
        if selected_date == datetime.datetime.now().date():
            timeslots = list(filter(lambda x: datetime.datetime.now().time() <= x, self.timepoints))

        none_callback_data = self._item_callback_data("None")
        for timepoint in timeslots:
            time_text = timepoint.strftime("%H:%M")
            time_callback_data = self._item_callback_data(time_text)

            available = timepoint in available_timepoints_to_select
            "available for selection; does take into account only remaining daily hours"
            blocked = timepoint in blocked_timepoints
            "timepoints that are blocked by already booked timepoints"
            already_selected = timepoint in endpoint_time_selected
            booked_by_someone = timepoint in already_booked_timepoints

            if already_selected:
                if timepoint == endpoint_time_selected[0]:
                    text = f"{time_text} -"
                elif timepoint == endpoint_time_selected[-1]:
                    text = f"- {time_text}"
                else:
                    assert_never(timepoint)
                keyboard_builer.button(text=text, callback_data=time_callback_data)
            elif available and not blocked:
                keyboard_builer.button(text=time_text, callback_data=time_callback_data)
            elif booked_by_someone:
                booking = already_booked_timepoints[timepoint]
                booked_by_alias = booking["participant_alias"]
                if booked_by_alias == manager.event.from_user.username:
                    keyboard_builer.button(text="🟢", callback_data=none_callback_data)
                else:
                    keyboard_builer.button(text="🔴", url=f"https://t.me/{booked_by_alias}")
            else:
                keyboard_builer.button(
                    text=" ",
                    callback_data=self._item_callback_data("None"),
                )
        keyboard_builer.adjust(4, True)
        return keyboard_builer.export()

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
        widget_data = self.get_widget_data(manager, [])
        if data == "None":
            if widget_data:
                self.set_widget_data(manager, [])
                return True
            return False
        clicked_timepoint = data

        # add or remove timeslot

        endpoint_timepoints = self.get_widget_data(manager, [])
        if clicked_timepoint in endpoint_timepoints:
            endpoint_timepoints.remove(clicked_timepoint)
        else:
            endpoint_timepoints.append(clicked_timepoint)
        for i in range(len(endpoint_timepoints)):
            if isinstance(endpoint_timepoints[i], (datetime.time,)):
                endpoint_timepoints[i] = endpoint_timepoints[i].isoformat()
        self.set_widget_data(manager, endpoint_timepoints)
        return True

    def get_selected_time_points(self, manager: DialogManager) -> list[datetime.time]:
        endpoint_time_selected = self.get_widget_data(manager, [])
        endpoint_time_selected = list(
            map(
                lambda x: datetime.datetime.strptime(x, "%H:%M").time(),
                endpoint_time_selected,
            )
        )
        return endpoint_time_selected

    def __init__(
        self,
        timepoints: list[datetime.time] | Callable[..., list[datetime.time]],
        id: Optional[str] = None,
        when: WhenCondition = None,
    ):
        super().__init__(id=id, when=when)
        self._timepoints = timepoints

    @property
    def timepoints(self) -> list[datetime.time]:
        if callable(self._timepoints):
            return self._timepoints()
        return self._timepoints
