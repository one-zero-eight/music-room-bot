from aiogram import types

kb = [
    [
        types.KeyboardButton(text="Создать бронь"),
        types.KeyboardButton(text="Посмотреть картинку с бронями"),
        types.KeyboardButton(text="Открыть личный кабинет"),
    ],
]

register = [
    [
        types.InlineKeyboardButton(text="Зарегистрироваться", callback_data="register"),
    ]
]
