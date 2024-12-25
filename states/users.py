from aiogram.dispatcher.filters.state import StatesGroup, State


class UserStates(StatesGroup):
    GET_FULL_NAME = State()
    GET_PHONE = State()
