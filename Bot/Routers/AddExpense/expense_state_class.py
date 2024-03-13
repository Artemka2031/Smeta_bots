from aiogram.fsm.state import StatesGroup, State


class Expense(StatesGroup):
    extra_messages = State()
    date_message_id = State()
    date = State()
    category_message_id = State()
    category = State()
    type = State()
    amount_message_id = State()
    amount = State()
    comment_message_id = State()
    comment = State()
