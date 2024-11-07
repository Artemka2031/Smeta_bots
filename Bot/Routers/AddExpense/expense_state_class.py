from aiogram.fsm.state import StatesGroup, State


class Expense(StatesGroup):
    extra_messages = State()
    date_message_id = State()
    date = State()

    wallet_message_id = State()
    wallet = State()
    creditor_borrow = State()
    creditor_return = State()

    chapter_message_id = State()
    chapter_code = State()
    category_code = State()
    subcategory_code = State()

    amount_message_id = State()
    amount = State()
    coefficient = State()

    comment_message_id = State()
    comment = State()
