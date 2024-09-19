from aiogram.fsm.state import StatesGroup, State


class Expense(StatesGroup):
    # Для работы с сообщениями и ввода данных
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

    # Новые поля для хранения данных из таблицы
    # Данные из столбца B (коды)
    column_b_values = State()
    # Данные из столбца C (названия)
    column_c_values = State()
    # Данные из пятой строки (даты)
    dates_row = State()
    # Все строки таблицы (полное содержание таблицы для гибкого использования)
    all_rows = State()
