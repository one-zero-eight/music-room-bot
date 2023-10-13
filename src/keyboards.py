from aiogram import types
from aiogram.filters.callback_data import CallbackData

menu = types.ReplyKeyboardMarkup(
    resize_keyboard=True,
    keyboard=[
        [
            types.KeyboardButton(text="Create a boooking"),
            types.KeyboardButton(text="Show the image with bookings"),
            types.KeyboardButton(text="Open profile"),
        ]
    ],
)


class MyCallbackData(CallbackData, prefix="some_prefix"):
    some_key: str


registration = types.InlineKeyboardMarkup(
    inline_keyboard=[
        [
            types.InlineKeyboardButton(
                text="Register", callback_data=MyCallbackData(some_key="register").pack()
            )
        ]
    ]
)

phone_request_kb = types.ReplyKeyboardMarkup(
    resize_keyboard=True,
    one_time_keyboard=True,
    keyboard=[[types.KeyboardButton(text="Share my phone number", request_contact=True)]],
)
