from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


class ChooseWalletCallback(CallbackData, prefix="CWC"):
    wallet: str


# Функция создания клавиатуры
def create_wallet_keyboard() -> InlineKeyboardMarkup:
    wallets = ["Проект", "Взять в долг", "Вернуть долг", "Дивиденды"]
    keyboard_builder = InlineKeyboardBuilder()

    for wallet in wallets:
        keyboard_builder.add(InlineKeyboardButton(
            text=wallet,
            callback_data=ChooseWalletCallback(wallet=wallet).pack()
        ))

    keyboard_builder.adjust(2)
    return keyboard_builder.as_markup()


class ChooseCreditorCallback(CallbackData, prefix="CWC"):
    creditor: str


def creditors_keyboard(creditors_list):
    keyboard_builder = InlineKeyboardBuilder()

    for creditor in creditors_list:
        keyboard_builder.add(InlineKeyboardButton(
            text=creditor,
            callback_data=ChooseCreditorCallback(creditor=creditor).pack()
        ))

    # Добавление кнопки "Назад"
    keyboard_builder.add(InlineKeyboardButton(
        text="<< Назад",
        callback_data=ChooseCreditorCallback(creditor="Назад").pack(),
    ))

    keyboard_builder.adjust(1)
    return keyboard_builder.as_markup()
