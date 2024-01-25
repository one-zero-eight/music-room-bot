from __future__ import annotations

from aiogram_dialog.widgets.kbd import Keyboard
from aiogram_dialog.widgets.kbd.calendar_kbd import CalendarDaysView, CalendarUserConfig, next_month_begin, get_today, \
    empty_button, ManagedCalendar, CalendarScopeView, CallbackGenerator, CalendarConfig, DATE_TEXT, TODAY_TEXT, \
    WEEK_DAY_TEXT, DAYS_HEADER_TEXT, ZOOM_OUT_TEXT, NEXT_MONTH_TEXT, PREV_MONTH_TEXT, CALLBACK_PREFIX_YEAR, \
    CALLBACK_PREFIX_MONTH, CalendarScope, CalendarData, BEARING_DATE, month_begin, CALLBACK_PREV_MONTH, \
    CALLBACK_NEXT_MONTH, MONTH_TEXT, THIS_MONTH_TEXT, MONTHS_HEADER_TEXT, NEXT_YEAR_TEXT, PREV_YEAR_TEXT, \
    CALLBACK_SCOPE_MONTHS, CALLBACK_SCOPE_YEARS, CALLBACK_NEXT_YEAR, CALLBACK_PREV_YEAR, THIS_YEAR_TEXT, YEAR_TEXT, \
    NEXT_YEARS_PAGE_TEXT, PREV_YEARS_PAGE_TEXT, CALLBACK_PREV_YEARS_PAGE, CALLBACK_NEXT_YEARS_PAGE, OnDateSelected, \
    CalendarMonthView, CalendarYearsView

from datetime import date, datetime, timedelta
from typing import (
    Dict, List, Optional, Union,
)

from aiogram.types import CallbackQuery, InlineKeyboardButton

from aiogram_dialog.api.protocols import DialogManager, DialogProtocol
from aiogram_dialog.widgets.common import WhenCondition
from aiogram_dialog.widgets.text import Text
from aiogram_dialog.widgets.widget_event import (
    ensure_event_processor, WidgetEventProcessor,
)


class CustomCalendarDaysView(CalendarDaysView):
    def __init__(self, callback_generator: CallbackGenerator, config: CalendarConfig, date_text: Text = DATE_TEXT,
                 today_text: Text = TODAY_TEXT, weekday_text: Text = WEEK_DAY_TEXT,
                 header_text: Text = DAYS_HEADER_TEXT, zoom_out_text: Text = ZOOM_OUT_TEXT,
                 next_month_text: Text = NEXT_MONTH_TEXT, prev_month_text: Text = PREV_MONTH_TEXT):
        super().__init__(callback_generator, config, date_text, today_text, weekday_text, header_text, zoom_out_text,
                         next_month_text, prev_month_text)
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


class Calendar(Keyboard):
    """
    Calendar widget.

    Used to render keyboard for date selection.
    """

    def __init__(
            self,
            id: str,
            on_click: Union[OnDateSelected, WidgetEventProcessor, None] = None,
            config: Optional[CalendarConfig] = None,
            when: WhenCondition = None,
    ) -> None:
        """
        Init calendar widget.

        :param id: ID of widget
        :param on_click: Function to handle date selection
        :param config: Calendar configuration
        :param when: Condition when to show widget
        """
        super().__init__(id=id, when=when)
        self.on_click = ensure_event_processor(on_click)
        if config is None:
            config = CalendarConfig()
        self.config = config
        self.views = self._init_views()
        self._handlers = {
            CALLBACK_NEXT_MONTH: self._handle_next_month,
            CALLBACK_PREV_MONTH: self._handle_prev_month,
            CALLBACK_NEXT_YEAR: self._handle_next_year,
            CALLBACK_PREV_YEAR: self._handle_prev_year,
            CALLBACK_NEXT_YEARS_PAGE: self._handle_next_years_page,
            CALLBACK_PREV_YEARS_PAGE: self._handle_prev_years_page,
            CALLBACK_SCOPE_MONTHS: self._handle_scope_months,
            CALLBACK_SCOPE_YEARS: self._handle_scope_years,
        }

    def _init_views(self) -> Dict[CalendarScope, CalendarScopeView]:
        """
        Calendar scopes view initializer.

        Override this method customize how calendar is rendered.
        You can either set Text widgets for buttons in default views or
        create own implementation of views
        """
        return {
            CalendarScope.DAYS:
                CustomCalendarDaysView(self._item_callback_data, self.config),
            CalendarScope.MONTHS:
                CalendarMonthView(self._item_callback_data, self.config),
            CalendarScope.YEARS:
                CalendarYearsView(self._item_callback_data, self.config),
        }

    async def _get_user_config(
            self,
            data: Dict,
            manager: DialogManager,
    ) -> CalendarUserConfig:
        """
        User related config getter.

        Override this method to customize how user config is retrieved.

        :param data: data from window getter
        :param manager: dialog manager instance
        :return:
        """
        return CalendarUserConfig()

    async def _render_keyboard(
            self,
            data,
            manager: DialogManager,
    ) -> List[List[InlineKeyboardButton]]:
        scope = self.get_scope(manager)
        view = self.views[scope]
        offset = self.get_offset(manager)
        config = await self._get_user_config(data, manager)
        if offset is None:
            offset = get_today(config.timezone)
            self.set_offset(offset, manager)
        return await view.render(config, offset, data, manager)

    def get_scope(self, manager: DialogManager) -> CalendarScope:
        calendar_data: CalendarData = self.get_widget_data(manager, {})
        current_scope = calendar_data.get("current_scope")
        if not current_scope:
            return CalendarScope.DAYS
        try:
            return CalendarScope(current_scope)
        except ValueError:
            # LOG
            return CalendarScope.DAYS

    def get_offset(self, manager: DialogManager) -> Optional[date]:
        calendar_data: CalendarData = self.get_widget_data(manager, {})
        current_offset = calendar_data.get("current_offset")
        if current_offset is None:
            return None
        return date.fromisoformat(current_offset)

    def set_offset(self, new_offset: date,
                   manager: DialogManager) -> None:
        data = self.get_widget_data(manager, {})
        data["current_offset"] = new_offset.isoformat()

    def set_scope(self, new_scope: CalendarScope,
                  manager: DialogManager) -> None:
        data = self.get_widget_data(manager, {})
        data["current_scope"] = new_scope.value

    def managed(self, manager: DialogManager) -> "ManagedCalendar":
        return ManagedCalendar(self, manager)

    async def _handle_scope_months(
            self, data: str, manager: DialogManager,
    ) -> None:
        self.set_scope(CalendarScope.MONTHS, manager)

    async def _handle_scope_years(
            self, data: str, manager: DialogManager,
    ) -> None:
        self.set_scope(CalendarScope.YEARS, manager)

    async def _handle_prev_month(
            self, data: str, manager: DialogManager,
    ) -> None:
        offset = self.get_offset(manager)
        offset = month_begin(month_begin(offset) - timedelta(days=1))
        self.set_offset(offset, manager)

    async def _handle_next_month(
            self, data: str, manager: DialogManager,
    ) -> None:
        offset = self.get_offset(manager)
        offset = next_month_begin(offset)
        self.set_offset(offset, manager)

    async def _handle_prev_year(
            self, data: str, manager: DialogManager,
    ) -> None:
        offset = self.get_offset(manager)
        offset = offset.replace(offset.year - 1)
        self.set_offset(offset, manager)

    async def _handle_next_year(
            self, data: str, manager: DialogManager,
    ) -> None:
        offset = self.get_offset(manager)
        offset = offset.replace(offset.year + 1)
        self.set_offset(offset, manager)

    async def _handle_prev_years_page(
            self, data: str, manager: DialogManager,
    ) -> None:
        offset = self.get_offset(manager)
        offset = offset.replace(offset.year - self.config.years_per_page)
        self.set_offset(offset, manager)

    async def _handle_next_years_page(
            self, data: str, manager: DialogManager,
    ) -> None:
        offset = self.get_offset(manager)
        offset = offset.replace(offset.year + self.config.years_per_page)
        self.set_offset(offset, manager)

    async def _handle_click_month(
            self, data: str, manager: DialogManager,
    ) -> None:
        offset = self.get_offset(manager)
        month = int(data[len(CALLBACK_PREFIX_MONTH):])
        offset = date(offset.year, month, 1)
        self.set_offset(offset, manager)
        self.set_scope(CalendarScope.DAYS, manager)

    async def _handle_click_year(
            self, data: str, manager: DialogManager,
    ) -> None:
        year = int(data[len(CALLBACK_PREFIX_YEAR):])
        offset = date(year, 1, 1)
        self.set_offset(offset, manager)
        self.set_scope(CalendarScope.MONTHS, manager)

    async def _handle_click_date(
            self, data: str, manager: DialogManager,
    ) -> None:
        raw_date = int(data)
        await self.on_click.process_event(
            manager.event,
            self.managed(manager),
            manager,
            date.fromtimestamp(raw_date),
        )

    async def _process_item_callback(
            self,
            callback: CallbackQuery,
            data: str,
            dialog: DialogProtocol,
            manager: DialogManager,
    ) -> bool:
        if data in self._handlers:
            handler = self._handlers[data]
        elif data.startswith(CALLBACK_PREFIX_MONTH):
            handler = self._handle_click_month
        elif data.startswith(CALLBACK_PREFIX_YEAR):
            handler = self._handle_click_year
        else:
            handler = self._handle_click_date
        await handler(data, manager)
        return True
