from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import (
    Dict, List,
)

from aiogram.types import InlineKeyboardButton

from aiogram_dialog.api.protocols import DialogManager
from aiogram_dialog.widgets.kbd import Calendar
from aiogram_dialog.widgets.kbd.calendar_kbd import CalendarDaysView, CalendarUserConfig, next_month_begin, get_today, \
    empty_button


class CustomCalendarDaysView(CalendarDaysView):
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
        max_date = min(self.config.max_date, end_date)
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
                    row.append(await self._render_date_button(
                        current_date, today, data, manager,
                    ))
                else:
                    row.append(empty_button())
            keyboard.append(row)
        return keyboard


class CustomCalendar(Calendar):
    ...
