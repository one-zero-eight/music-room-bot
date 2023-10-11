import aiohttp
from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message

router = Router()


class Registration(StatesGroup):
    enter_email = State()
    enter_code = State()


@router.message(Command("start"))
async def start_registration(msg: Message, state: FSMContext):
    await msg.answer("Здравствуйте! Введите почту, на нее придет одноразовый код для регистрации/авторизации.")
    await state.set_state(Registration.enter_email)


@router.message(Registration.enter_email)
async def enter_email(message: Message, state: FSMContext):
    async with aiohttp.ClientSession() as session:
        url = "http://127.0.0.1:8000/auth/registration"
        params = {"email": message.text}
        async with session.post(url, params=params) as response:
            await response.text()
        await state.update_data(entered_email=message.text)
        await message.answer(text="Спасибо. Теперь введите полученный код")
        await state.set_state(Registration.enter_code)


@router.message(Registration.enter_code)
async def entered_code(message: Message, state: FSMContext):
    user_data = await state.get_data()
    entered_email = user_data.get("entered_email")
    url = "http://127.0.0.1:8000/auth/validate_code"
    params = {"email": entered_email, "code": message.text}
    async with aiohttp.ClientSession() as session:
        async with session.post(url, params=params) as response:
            await response.text()
            if response.status == 200:
                await message.answer(
                    text="Ваш код принят. Чтобы пользоваться муз. комнатой, вам предстоит заполнить профиль")
                await state.clear()
                await state.update_data(entered_code=message.text)
            else:
                await message.answer(text="Код неверный")
