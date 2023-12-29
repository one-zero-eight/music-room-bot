from aiogram import types
from aiogram.filters.callback_data import CallbackData

menu = types.ReplyKeyboardMarkup(
    resize_keyboard=True,
    keyboard=[
        [
            types.KeyboardButton(text="Create a booking"),
            types.KeyboardButton(text="Show the image with bookings"),
            types.KeyboardButton(text="My bookings"),
        ]
    ],
)


class RegistrationCallbackData(CallbackData, prefix="registration"):
    key: str


class ImageScheduleCallbackData(CallbackData, prefix="schedule"):
    key: str


registration = types.InlineKeyboardMarkup(
    inline_keyboard=[
        [types.InlineKeyboardButton(text="Register", callback_data=RegistrationCallbackData(key="register").pack())]
    ]
)

phone_request_kb = types.ReplyKeyboardMarkup(
    resize_keyboard=True,
    one_time_keyboard=True,
    keyboard=[[types.KeyboardButton(text="Share my phone number", request_contact=True)]],
)

confirm_email_kb = types.InlineKeyboardMarkup(
    inline_keyboard=[
        [
            types.InlineKeyboardButton(text="Yes", callback_data=RegistrationCallbackData(key="correct_email").pack()),
            types.InlineKeyboardButton(
                text="Change email", callback_data=RegistrationCallbackData(key="change_email").pack()
            ),
        ]
    ]
)

image_schedule_kb = types.InlineKeyboardMarkup(
    inline_keyboard=[
        [
            types.InlineKeyboardButton(
                text="Current", callback_data=ImageScheduleCallbackData(key="current_week").pack()
            ),
            types.InlineKeyboardButton(text="Next", callback_data=ImageScheduleCallbackData(key="next_week").pack()),
        ]
    ]
)
