import asyncio
import time

from aiogram import F, types, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from src.api import client
from src.constants import (
    rules_message,
    rules_confirmation_message,
    instructions_url,
    how_to_get_url,
    tg_chat_url,
)
from src.filters import RegisteredUserFilter
from src.menu import menu_kb
from src.routers.registration import router
from src.routers.registration.keyboards import (
    RegistrationCallbackData,
    phone_request_kb,
    confirm_email_kb,
    resend_code_kb,
    are_equal_keyboards,
)
from src.routers.registration.states import RegistrationStates
from src.routers.registration.utils import is_cyrillic


@router.callback_query(
    RegistrationCallbackData.filter(F.key == "register"), ~RegisteredUserFilter()
)
async def user_want_to_register(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.answer()
    await callback_query.bot.send_message(
        chat_id=callback_query.from_user.id,
        text="Enter your email. You will receive a one-time code for registration.",
    )
    await state.set_state(RegistrationStates.email_requested)


@router.callback_query(
    RegistrationCallbackData.filter(F.key == "register"), RegisteredUserFilter()
)
async def user_want_to_register_but_registered(callback_query: types.CallbackQuery):
    await callback_query.bot.send_message(
        chat_id=callback_query.from_user.id,
        text="You're already registered.",
        reply_markup=menu_kb,
    )


@router.message(RegistrationStates.email_requested, ~RegisteredUserFilter())
async def request_email(message: Message, state: FSMContext):
    m = await message.answer(
        text=f"You entered {message.text}. Is it correct email?",
        reply_markup=confirm_email_kb,
    )
    await state.update_data(email=message.text, request_email_message_id=m.message_id)


@router.callback_query(
    RegistrationCallbackData.filter(F.key == "change_email"), ~RegisteredUserFilter()
)
async def change_email(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.answer("Please enter your email again.")
    await state.set_state(RegistrationStates.email_requested)


@router.callback_query(
    RegistrationCallbackData.filter(F.key == "correct_email"), ~RegisteredUserFilter()
)
async def send_code(callback: types.CallbackQuery, state: FSMContext):
    if not are_equal_keyboards(callback.message.reply_markup, resend_code_kb):
        await callback.message.edit_reply_markup(reply_markup=resend_code_kb)
    user_data = await state.get_data()
    last_click = user_data.get(
        "last_click", time.mktime((1970, 1, 1, 0, 0, 0, 0, 0, 0))
    )
    difference_seconds: int = round(time.time() - last_click)

    if difference_seconds > 60:
        user_data = await state.get_data()
        email = user_data.get("email")
        success, error = await client.start_registration(email)
        if not success:
            await callback.message.answer(error)
        else:
            await callback.message.answer(
                "We sent a one-time code on your email. Please, enter it."
            )
            await state.set_state(RegistrationStates.code_requested)
        await state.update_data(last_click=time.time())
        await callback.answer()
    else:
        await callback.answer(
            text=f"You can send code once in a minute. {60 - difference_seconds} seconds left."
        )


@router.message(RegistrationStates.code_requested, ~RegisteredUserFilter())
async def request_code(message: types.Message, state: FSMContext, bot: Bot):
    user_data = await state.get_data()
    email = user_data.get("email")
    telegram_id = str(message.from_user.id)
    code = message.text

    success, error = await client.validate_code(email, code, telegram_id)

    if not success:
        await message.answer(error)
    else:
        request_email_message_id = user_data.get("request_email_message_id")
        if request_email_message_id:
            await bot.edit_message_text(
                text=f"Your email {email} is verified.",
                chat_id=message.chat.id,
                message_id=request_email_message_id,
                reply_markup=None,
            )

        await message.answer(
            text="Your code has been accepted. To use the music room, you need to fill out your profile."
        )
        await asyncio.sleep(0.1)
        await message.answer(
            text="Please provide access to your phone number.",
            reply_markup=phone_request_kb,
        )
        await state.set_state(RegistrationStates.phone_number_requested)


@router.message(RegistrationStates.phone_number_requested, F.contact)
async def request_phone_number(message: Message, state: FSMContext):
    phone_number = message.contact.phone_number
    await state.update_data(phone_number=phone_number)
    await message.answer(
        "Please, enter your fullname <b>in Russian</b>. <i>\nExample: Петров Иван Иванович</i>",
        parse_mode="HTML",
    )
    await state.set_state(RegistrationStates.name_requested)


@router.message(RegistrationStates.name_requested)
async def request_name(message: Message, state: FSMContext):
    if not await is_cyrillic(message.text):
        await message.answer(
            "Please, enter a valid fullname <b>in Russian</b>. <i>\nExample: Петров Иван Иванович</i>",
            parse_mode="HTML",
        )
    else:
        user_data = await state.get_data()

        success, error = await client.fill_profile(
            telegram_id=message.from_user.id,
            name=message.text,
            alias=message.from_user.username,
            phone_number=user_data.get("phone_number"),
        )

        if not success:
            await message.answer(error)
        else:
            await state.update_data(name=message.text)

            await message.answer(
                "Please, read the rules and confirm that you agree with them."
            )
            await asyncio.sleep(0.1)
            confirm_kb = types.ReplyKeyboardMarkup(
                keyboard=[
                    [
                        types.KeyboardButton(
                            text=rules_confirmation_message,
                        )
                    ]
                ],
                resize_keyboard=True,
                one_time_keyboard=True,
            )
            await message.answer(rules_message, reply_markup=confirm_kb)
            await state.set_state(RegistrationStates.rules_confirmation_requested)


@router.message(RegistrationStates.rules_confirmation_requested)
async def confirm_rules(message: Message, state: FSMContext):
    if (
        message.text[:100]
        == rules_confirmation_message.format(name=(await state.get_data()))[:100]
    ):
        await message.answer("You have successfully registered.", reply_markup=menu_kb)

        keyboard = types.InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    types.InlineKeyboardButton(
                        text="Instructions", url=instructions_url
                    ),
                    types.InlineKeyboardButton(text="Location", url=how_to_get_url),
                    types.InlineKeyboardButton(text="Telegram chat", url=tg_chat_url),
                ]
            ]
        )

        await message.answer(
            "If you have any questions, you can ask them in the chat or read the instructions.",
            reply_markup=keyboard,
        )

        await state.clear()
    else:
        await message.answer("You haven't confirmed the rules. Please, try again.")
