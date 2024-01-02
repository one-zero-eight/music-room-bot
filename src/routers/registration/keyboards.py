from aiogram import types
from aiogram.filters.callback_data import CallbackData


class RegistrationCallbackData(CallbackData, prefix="registration"):
    key: str


registration_kb = types.InlineKeyboardMarkup(
    inline_keyboard=[
        [
            types.InlineKeyboardButton(
                text="Register",
                callback_data=RegistrationCallbackData(key="register").pack(),
            )
        ]
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
            types.InlineKeyboardButton(
                text="Yes",
                callback_data=RegistrationCallbackData(key="correct_email").pack(),
            ),
            types.InlineKeyboardButton(
                text="Change email",
                callback_data=RegistrationCallbackData(key="change_email").pack(),
            ),
        ]
    ]
)
