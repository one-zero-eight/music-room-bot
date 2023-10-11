import aiohttp
from aiogram import F, Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message

from keyboards.main_menu import kb, register

router = Router()


class Registration(StatesGroup):
    enter_email = State()
    enter_code = State()
    enter_name_and_necessary_cred = State()
    enter_phone_number = State()


@router.message(F.text == "register")
async def start_registration(msg: Message, state: FSMContext):
    await msg.answer("Введите почту, на нее придет одноразовый код для регистрации/авторизации.")
    await state.set_state(Registration.enter_email)


@router.message(Registration.enter_email)
async def enter_email(message: Message, state: FSMContext):
    async with aiohttp.ClientSession() as session:
        url = "http://127.0.0.1:8000/auth/registration"
        params = {"email": message.text}
        async with session.post(url, params=params) as response:
            await response.text()
            if response.status == 400:
                await message.answer(text="Пользователь с указанной почтой уже зарегистрирован.")
            else:
                await state.update_data(email=message.text)
                await message.answer(text="Спасибо. Теперь введите полученный код")
                await state.set_state(Registration.enter_code)


@router.message(Registration.enter_code)
async def entered_code(message: Message, state: FSMContext):
    user_data = await state.get_data()
    email = user_data.get("email")
    url = "http://127.0.0.1:8000/auth/validate_code"
    params = {"email": email, "code": message.text}
    async with aiohttp.ClientSession() as session:
        async with session.post(url, params=params) as response:
            await response.text()
            if response.status == 200:
                await message.answer(
                    text="Ваш код принят. Чтобы пользоваться муз. комнатой, вам предстоит заполнить профиль."
                )
                await message.answer(text="Введите ваше имя")
                await state.set_state(Registration.enter_name_and_necessary_cred)

            else:
                await message.answer(text="Код неверный")


@router.message(Registration.enter_phone_number)
async def entered_phone_number(message: Message, state: FSMContext):
    await state.set_state(Registration.enter_name_and_necessary_cred)


@router.message(Registration.enter_name_and_necessary_cred)
async def enter_name_and_necessary_credentials(message: Message, state: FSMContext):
    user_data = await state.get_data()
    params = {
        "email": user_data.get("email"),
        "name": message.text,
        "telegram_id": str(message.from_user.id),
        "alias": str(message.from_user.username),
        "phone_number": user_data.get("phone_number"),
    }
    url = "http://127.0.0.1:8000/participants/fill_profile"
    async with aiohttp.ClientSession() as session:
        async with session.post(url, params=params) as response:
            await response.text()

    await message.answer(text="Нам потребуется получить ваш номер телефона. Он будет зашифрован.")
    await state.clear()


@router.message(Command("start"))
async def start(message: types.Message):
    telegram_id = str(message.from_user.id)
    res = await is_user_exists(telegram_id)
    if res:
        keyboard = types.ReplyKeyboardMarkup(
            keyboard=kb, resize_keyboard=True, input_field_placeholder="Выберите действие"
        )
        await message.answer("Добро пожаловать! Выберете интересующее вас действие.", reply_markup=keyboard)
    else:
        keyboard1 = types.InlineKeyboardMarkup(inline_keyboard=register)
        await message.answer(
            "Добро пожаловать! Чтобы продолжить, вам необходимо зарегистрироваться.", reply_markup=keyboard1)


async def is_user_exists(telegram_id: str) -> bool:
    url = f"http://127.0.0.1:8000/participants/is_user_exists"
    params = {"telegram_id": telegram_id}
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as response:
            response_text = await response.text()
            return False if response_text == "false" else True
