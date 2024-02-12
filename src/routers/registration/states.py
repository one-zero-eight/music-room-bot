from aiogram.fsm.state import StatesGroup, State


class RegistrationStates(StatesGroup):
    email_requested = State()
    code_requested = State()
    phone_number_requested = State()
    name_requested = State()
    rules_confirmation_requested = State()


class RefillProfileStates(StatesGroup):
    name_requested = State()
    phone_number_requested = State()
