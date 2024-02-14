from __future__ import annotations

from aiogram_dialog.widgets.kbd.calendar_kbd import (
    CalendarDaysView,
    CalendarUserConfig,
    next_month_begin,
    get_today,
    empty_button,
    CalendarScopeView,
    CallbackGenerator,
    CalendarConfig,
    DATE_TEXT,
    TODAY_TEXT,
    WEEK_DAY_TEXT,
    DAYS_HEADER_TEXT,
    ZOOM_OUT_TEXT,
    NEXT_MONTH_TEXT,
    PREV_MONTH_TEXT,
    CalendarScope,
    CalendarMonthView,
    CalendarYearsView,
    Calendar,
)

from datetime import date, datetime, timedelta
from typing import (
    Dict,
    List,
)

from aiogram.types import InlineKeyboardButton

from aiogram_dialog.api.protocols import DialogManager
from aiogram_dialog.widgets.text import Text


class CustomCalendarDaysView(CalendarDaysView):
    def __init__(
        self,
        callback_generator: CallbackGenerator,
        config: CalendarConfig,
        date_text: Text = DATE_TEXT,
        today_text: Text = TODAY_TEXT,
        weekday_text: Text = WEEK_DAY_TEXT,
        header_text: Text = DAYS_HEADER_TEXT,
        zoom_out_text: Text = ZOOM_OUT_TEXT,
        next_month_text: Text = NEXT_MONTH_TEXT,
        prev_month_text: Text = PREV_MONTH_TEXT,
    ):
        super().__init__(
            callback_generator,
            config,
            date_text,
            today_text,
            weekday_text,
            header_text,
            zoom_out_text,
            next_month_text,
            prev_month_text,
        )
        self.config = config
        self.zoom_out_text = zoom_out_text
        self.next_month_text = next_month_text
        self.prev_month_text = prev_month_text
        self.callback_generator = callback_generator
        self.date_text = date_text
        self.today_text = today_text
        self.weekday_text = weekday_text
        self.header_text = header_text

    async def _render_days(
        self,
        config: CalendarUserConfig,
        offset: date,
        data: Dict,
        manager: DialogManager,
    ) -> List[List[InlineKeyboardButton]]:
        keyboard = []
        # align beginning
        start_date = offset.replace(day=1)  # month beginning
        min_date = max(self.config.min_date, start_date)
        days_since_week_start = start_date.weekday() - config.firstweekday
        if days_since_week_start < 0:
            days_since_week_start += 7
        start_date -= timedelta(days=days_since_week_start)
        end_date = next_month_begin(offset) - timedelta(days=1)
        # align ending
        max_date = min(self.config.max_date, end_date, datetime.now().date() + timedelta(7))
        days_since_week_start = end_date.weekday() - config.firstweekday
        days_till_week_end = (6 - days_since_week_start) % 7
        end_date += timedelta(days=days_till_week_end)
        # add days
        today = get_today(config.timezone)
        for offset in range(0, (end_date - start_date).days, 7):
            row = []
            for row_offset in range(7):
                days_offset = timedelta(days=(offset + row_offset))
                current_date = start_date + days_offset
                if min_date <= current_date <= max_date and current_date >= datetime.now().date():
                    row.append(
                        await self._render_date_button(
                            current_date,
                            today,
                            data,
                            manager,
                        )
                    )
                else:
                    row.append(empty_button())
            keyboard.append(row)
        return keyboard


class CustomCalendar(Calendar):
    """
    Calendar widget.

    Used to render keyboard for date selection.
    """

    def _init_views(self) -> Dict[CalendarScope, CalendarScopeView]:
        """
        Calendar scopes view initializer.

        Override this method customize how calendar is rendered.
        You can either set Text widgets for buttons in default views or
        create own implementation of views
        """
        return {
            CalendarScope.DAYS: CustomCalendarDaysView(self._item_callback_data, self.config),
            CalendarScope.MONTHS: CalendarMonthView(self._item_callback_data, self.config),
            CalendarScope.YEARS: CalendarYearsView(self._item_callback_data, self.config),
        }
