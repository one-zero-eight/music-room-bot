from aiogram import types
from aiogram.filters.callback_data import CallbackData

menu = types.ReplyKeyboardMarkup(
    resize_keyboard=True,
    keyboard=[
        [
            types.KeyboardButton(text="Создать бронь"),
            types.KeyboardButton(text="Посмотреть картинку с бронями"),
            types.KeyboardButton(text="Открыть личный кабинет"),
        ]
    ],
)


class MyCallbackData(CallbackData, prefix="some_prefix"):
    some_key: str


registration = types.InlineKeyboardMarkup(
    inline_keyboard=[
        [
            types.InlineKeyboardButton(
                text="Зарегистрироваться", callback_data=MyCallbackData(some_key="register").pack()
            )
        ]
    ]
)

phone_request_kb = types.ReplyKeyboardMarkup(
    resize_keyboard=True,
    one_time_keyboard=True,
    keyboard=[[types.KeyboardButton(text="Share My Phone Number", request_contact=True)]],
)
