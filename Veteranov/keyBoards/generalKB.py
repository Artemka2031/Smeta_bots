from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton


def create_markup_rows(buttons):
    buttons = [button for button in buttons if button.text != ""]

    rows = []
    for idx, button in enumerate(buttons):
        if idx % 2 == 0:
            row = []
        row.append(button)
        if idx % 2 == 1 or idx == len(buttons) - 1:
            rows.append(row)
    return rows


def NO_KB():
    return ReplyKeyboardRemove()


def date_kb():
    date_kb = InlineKeyboardMarkup()
    date_kb.add(InlineKeyboardButton('Сегодня', callback_data='today'))

    return date_kb


def create_wallets_kb(wallets, message_id, wallet_choose) -> InlineKeyboardMarkup:
    wallets_kb = InlineKeyboardMarkup()
    [wallets_kb.add(InlineKeyboardButton(
        i, callback_data=wallet_choose.new(i, message_id))) for i in wallets]
    return wallets_kb


def create_creditors_borrow_kb(types, message_id, move, credititors_debt) -> InlineKeyboardMarkup:
    types_of_expence_kb = InlineKeyboardMarkup()

    buttons = [(InlineKeyboardButton(
        i, callback_data=credititors_debt.new(i, "В долг"))) for i in types]

    rows = create_markup_rows(buttons)

    [types_of_expence_kb.row(*row) for row in rows]

    types_of_expence_kb.add(InlineKeyboardButton(
        "<< Назад", callback_data=move.new("Назад", message_id)))

    return types_of_expence_kb


def create_creditors_return_kb(types, message_id, move, credititors_debt) -> InlineKeyboardMarkup:
    types_of_expence_kb = InlineKeyboardMarkup()

    buttons = [(InlineKeyboardButton(
        i, callback_data=credititors_debt.new(i, "Возврат"))) for i in types]

    rows = create_markup_rows(buttons)

    [types_of_expence_kb.row(*row) for row in rows]

    types_of_expence_kb.add(InlineKeyboardButton(
        "<< Назад", callback_data=move.new("Назад", message_id)))

    return types_of_expence_kb


def edit_or_delete_kb(expence_id, message_id, edit_or_delete) -> InlineKeyboardMarkup:
    # edit_button = InlineKeyboardButton("Изменить", callback_data=edit_or_delete.new("Edit", expence_id, message_id))
    delete_button = InlineKeyboardButton(
        "Удалить", callback_data=edit_or_delete.new("Delete", expence_id, message_id))
    # edit_kb = InlineKeyboardMarkup().add(edit_button, delete_button)
    edit_kb = InlineKeyboardMarkup().add(delete_button)

    return edit_kb

def edit_or_delete_coming_kb(expence_id, message_id, edit_or_delete) -> InlineKeyboardMarkup:
    # edit_button = InlineKeyboardButton("Изменить", callback_data=edit_or_delete.new("Edit", expence_id, message_id))
    delete_button = InlineKeyboardButton(
        "Удалить", callback_data=edit_or_delete.new("Coming del", expence_id, message_id))
    # edit_kb = InlineKeyboardMarkup().add(edit_button, delete_button)
    edit_kb = InlineKeyboardMarkup().add(delete_button)

    return edit_kb
