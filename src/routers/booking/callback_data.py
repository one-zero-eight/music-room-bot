from aiogram.filters.callback_data import CallbackData


class MyBookingsCallbackData(CallbackData, prefix="my_bookings"):
    key: str
    id: int = None
