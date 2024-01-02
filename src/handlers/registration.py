import asyncio

from aiogram import F, Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message

from src.api import client
from src.keyboards import (
    RegistrationCallbackData,
    confirm_email_kb,
    menu,
    phone_request_kb,
    registration,
)

router = Router()


class Registration(StatesGroup):
    email_requested = State()
    code_requested = State()
    phone_number_requested = State()
    name_requested = State()


@router.message(Command("start"))
async def start(message: types.Message):
    telegram_id = str(message.from_user.id)
    res = await client.is_user_exists(telegram_id)
    if res:
        await message.answer("Welcome! Choose the action you're interested in.", reply_markup=menu)
    else:
        await message.answer("Welcome! To continue, you need to register.", reply_markup=registration)


@router.callback_query(RegistrationCallbackData.filter(F.key == "register"))
async def user_want_to_register(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.answer()
    telegram_id = str(callback_query.from_user.id)
    if not await client.is_user_exists(telegram_id):
        await callback_query.bot.send_message(
            chat_id=callback_query.from_user.id,
            text="Enter your email. You will receive a one-time code for registration.",
        )
        await state.set_state(Registration.email_requested)
    else:
        await callback_query.bot.send_message(
            chat_id=callback_query.from_user.id,
            text="You`re already registered.",
            reply_markup=menu,
        )


@router.message(Registration.email_requested)
async def request_email(message: Message, state: FSMContext):
    await state.update_data(email=message.text)
    await message.answer(
        text=f"You entered {message.text}. Is it correct email?",
        reply_markup=confirm_email_kb,
    )


@router.callback_query(RegistrationCallbackData.filter(F.key == "change_email"))
async def change_email(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.answer("Please enter your email again.")
    await state.set_state(Registration.email_requested)


@router.callback_query(RegistrationCallbackData.filter(F.key == "correct_email"))
async def send_code(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    user_data = await state.get_data()
    email = user_data.get("email")
    success, error = await client.start_registration(email)
    if not success:
        await callback.message.answer(error)
    else:
        await callback.message.answer("We sent a one-time code on your email. Please, enter it.")
        await state.set_state(Registration.code_requested)


@router.message(Registration.code_requested)
async def request_code(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    email = user_data.get("email")
    telegram_id = str(message.from_user.id)
    code = message.text

    success, error = await client.validate_code(email, code, telegram_id)

    if not success:
        await message.answer(error)
    else:
        await message.answer(
            text="Your code has been accepted. To use the music room, you need to fill out your profile."
        )
        await asyncio.sleep(0.1)
        await message.answer(
            text="Please provide access to your phone.",
            reply_markup=phone_request_kb,
        )
        await state.set_state(Registration.phone_number_requested)


@router.message(Registration.phone_number_requested, F.contact)
async def request_phone_number(message: Message, state: FSMContext):
    phone_number = message.contact.phone_number
    await state.update_data(phone_number=phone_number)
    await message.answer("Please, enter your full name.")
    await state.set_state(Registration.name_requested)


@router.message(Registration.name_requested)
async def request_name(message: Message, state: FSMContext):
    user_data = await state.get_data()

    success, error = await client.fill_profile(
        name=message.text,
        email=user_data.get("email"),
        alias=message.from_user.username,
        phone_number=user_data.get("phone_number"),
    )

    if not success:
        await message.answer(error)
    else:
        await message.answer("You have successfully registered.", reply_markup=menu)
        await state.clear()
