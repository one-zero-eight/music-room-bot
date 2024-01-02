from aiogram.fsm.state import StatesGroup, State


class CreateBookingStates(StatesGroup):
    choose_date = State()
    choose_time = State()
