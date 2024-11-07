from datetime import datetime

from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


class TodayCallback(CallbackData, prefix="TDC"):
    today: str


def create_today_kb():
    today = datetime.today().strftime('%d.%m.%y')
    text = "Сегодня"
    builder = InlineKeyboardBuilder()
    builder.button(text=text, callback_data=TodayCallback(today=today).pack())
    return builder.as_markup()


class ChooseChapterCallback(CallbackData, prefix="CChaC"):
    chapter_code: str
    back: bool


def chapters_choose_kb(chapters):
    chapters_b = InlineKeyboardBuilder()

    for code, name in chapters.items():
        callback_data = ChooseChapterCallback(chapter_code=code, back=False).pack()
        chapters_b.add(InlineKeyboardButton(text=name, callback_data=callback_data))

    # Добавление кнопки "Назад"
    chapters_b.add(InlineKeyboardButton(text="<< Назад",
                                        callback_data=ChooseChapterCallback(chapter_code=" ",
                                                                            back=True).pack()))

    chapters_b.adjust(1)

    return chapters_b.as_markup()


class ChooseCategoryCallback(CallbackData, prefix="CCatC"):
    category_code: str
    back: bool


def category_choose_kb(categories):
    category_b = InlineKeyboardBuilder()

    for category_id, category_name in categories.items():
        category_b.add(InlineKeyboardButton(
            text=category_name,
            callback_data=ChooseCategoryCallback(category_code=category_id,
                                                 back=False).pack()
        ))

    # Добавление кнопки "Назад"
    category_b.add(InlineKeyboardButton(
        text="<< Назад",
        callback_data=ChooseCategoryCallback(category_code="", back=True).pack(),
    ))

    category_b.adjust(1)
    return category_b.as_markup()


class ChooseSubCategoryCallback(CallbackData, prefix="CSubCatC"):
    subcategory_code: str
    back: bool


def subcategory_choose_kb(subcategories):
    subcategory_b = InlineKeyboardBuilder()

    for subcategory_code, subcategory_name in subcategories.items():
        subcategory_b.add(InlineKeyboardButton(
            text=subcategory_name,
            callback_data=ChooseSubCategoryCallback(subcategory_code=subcategory_code, back=False).pack()
        ))

    # Добавление кнопки "Назад"
    subcategory_b.add(InlineKeyboardButton(
        text="<< Назад",
        callback_data=ChooseSubCategoryCallback(subcategory_code="", back=True).pack(),
    ))

    subcategory_b.adjust(1)
    return subcategory_b.as_markup()
