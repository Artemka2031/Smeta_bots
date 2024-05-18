from aiogram.fsm.state import StatesGroup, State


class Coming(StatesGroup):
    extra_messages = State()
    date_message_id = State()
    date = State()

    coming_message_id = State()
    coming_code = State()

    amount_message_id = State()
    amount = State()

    comment_message_id = State()
    comment = State()
