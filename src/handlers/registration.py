import asyncio

import aiohttp
from aiogram import F, Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message

from src.keyboards import MyCallbackData, menu, phone_request_kb, registration

router = Router()


@router.message(Command("start"))
async def start(message: types.Message):
    telegram_id = str(message.from_user.id)
    res = await is_user_exists(telegram_id)
    if res:
        await message.answer("Welcome! Choose the action you're interested in.", reply_markup=menu)
    else:
        await message.answer("Welcome! To continue, you need to register.", reply_markup=registration)


class Registration(StatesGroup):
    enter_email = State()
    enter_code = State()
    request_phone_number = State()
    enter_name_and_necessary_credentials = State()


@router.callback_query(MyCallbackData.filter(F.some_key == "register"))
async def callback(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.answer()  # Removes the loading icon from the button (hourglass)
    await callback_query.bot.send_message(
        chat_id=callback_query.from_user.id,
        text="Enter your email. You will receive a one-time code for registration/authentication.",
    )
    await state.set_state(Registration.enter_email)


@router.message(Registration.enter_email)
async def enter_email(message: Message, state: FSMContext):
    async with aiohttp.ClientSession() as session:
        url = "http://127.0.0.1:8000/auth/registration"
        params = {"email": message.text}
        async with session.post(url, params=params) as response:
            await response.text()
            if response.status == 400:
                await message.answer(text="A user with the provided email is already registered.")
            else:
                await state.update_data(email=message.text)
                await message.answer(text="Enter the received code")
                await state.set_state(Registration.enter_code)


@router.message(Registration.enter_code)
async def enter_code(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    email = user_data.get("email")
    telegram_id = str(message.from_user.id)

    url = "http://127.0.0.1:8000/auth/validate_code"
    params = {"email": email, "code": message.text, "telegram_id": telegram_id}
    async with aiohttp.ClientSession() as session:
        async with session.post(url, params=params) as response:
            await response.text()
            if response.status == 200:
                await message.answer(
                    text="Your code has been accepted. To use the music room, you need to fill out your profile."
                )
                await asyncio.sleep(0.5)
                await message.answer(
                    text="Please provide access to your phone",
                    reply_markup=phone_request_kb,
                )
                await state.set_state(Registration.request_phone_number)
            else:
                await message.answer("Incorrect code")


@router.message(Registration.request_phone_number, F.contact)
async def request_phone_number(message: Message, state: FSMContext):
    phone_number = message.contact.phone_number
    await state.update_data(phone_number=phone_number)
    await message.answer("Enter your name")
    await state.set_state(Registration.enter_name_and_necessary_credentials)


@router.message(Registration.enter_name_and_necessary_credentials)
async def enter_name_and_necessary_credentials(message: Message, state: FSMContext):
    user_data = await state.get_data()
    params = {
        "name": str(message.text),
        "email": str(user_data.get("email")),
        "alias": str(message.from_user.username),
        "phone_number": str(user_data.get("phone_number")),
    }
    url = "http://127.0.0.1:8000/participants/fill_profile"
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=params) as response:
            await response.text()
            if response.status == 200:
                await message.answer("You have successfully registered.", reply_markup=menu)
            else:
                await message.answer("There was an error during registration.")
    await state.clear()


async def is_user_exists(telegram_id: str) -> bool:
    url = f"http://127.0.0.1:8000/auth/is_user_exists"
    params = {"telegram_id": telegram_id}
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as response:
            response_text = await response.text()
            return False if response_text == "false" else True
