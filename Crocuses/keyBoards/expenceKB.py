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


def create_expence_categories_kb(categories, message_id, category_choose) -> InlineKeyboardMarkup:
    categories_of_expence_kb = InlineKeyboardMarkup()
    [categories_of_expence_kb.add(InlineKeyboardButton(
        i, callback_data=category_choose.new(i, message_id))) for i in categories]

    return categories_of_expence_kb

def create_expence_categories_kb_without_debt(categories, message_id, category_choose)-> InlineKeyboardMarkup:
    categories_of_expence_kb = InlineKeyboardMarkup()
    categories_to_add = categories[:-1]
    [categories_of_expence_kb.add(InlineKeyboardButton(i, callback_data=category_choose.new(i, message_id))) for i in categories_to_add]

    return categories_of_expence_kb


def create_expence_types_kb_for_debt(types, message_id, move, type_choose) -> InlineKeyboardMarkup:
    types_of_expence_kb = InlineKeyboardMarkup()
    buttons = [InlineKeyboardButton(
        i, callback_data=type_choose.new("Возврат", i)) for i in types]

    rows = create_markup_rows(buttons)

    [types_of_expence_kb.row(*row) for row in rows]

    types_of_expence_kb.add(InlineKeyboardButton(
        "<< Назад", callback_data=move.new("Назад", message_id)))

    return types_of_expence_kb


def create_expence_types_kb(types, message_id, move, type_choose) -> InlineKeyboardMarkup:
    types_of_expence_kb = InlineKeyboardMarkup()
    buttons = [InlineKeyboardButton(
        i, callback_data=type_choose.new("", i)) for i in types]

    rows = create_markup_rows(buttons)

    [types_of_expence_kb.row(*row) for row in rows]

    types_of_expence_kb.add(InlineKeyboardButton(
        "<< Назад", callback_data=move.new("Назад", message_id)))

    return types_of_expence_kb


def сoeff_kb():
    сoeff_kb = InlineKeyboardMarkup().row(
        InlineKeyboardButton("0,9", callback_data="0,90"),
        InlineKeyboardButton("1,05", callback_data="1,05")
    )

    return сoeff_kb


def edit_expence_kb(chat_id, message_id, cd_edit_byid) -> InlineKeyboardMarkup:
    edit_button = InlineKeyboardButton(
        "Изменить", callback_data=cd_edit_byid.new(chat_id, message_id))
    edit_kb = InlineKeyboardMarkup().add(edit_button)

    return edit_kb


def edit_kb(message_id, expence_id, to_edit):
    edit_kb = InlineKeyboardMarkup().row(
        InlineKeyboardButton("Кошелёк", callback_data=to_edit.new(
            message_id, expence_id, "wallet")),
        InlineKeyboardButton("Тип", callback_data=to_edit.new(
            message_id, expence_id, "type_of_expense")),
        InlineKeyboardButton("Сумма", callback_data=to_edit.new(
            message_id, expence_id, "ammount"))
    ).add(
        InlineKeyboardButton("<<Назад", callback_data=to_edit.new(
            message_id, expence_id, "Назад"))
    )

    return edit_kb
