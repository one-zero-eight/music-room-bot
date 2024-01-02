from aiogram import types

menu_kb = types.ReplyKeyboardMarkup(
    resize_keyboard=True,
    keyboard=[
        [
            types.KeyboardButton(text="Create a booking"),
            types.KeyboardButton(text="Show the image with bookings"),
            types.KeyboardButton(text="My bookings"),
        ]
    ],
)
