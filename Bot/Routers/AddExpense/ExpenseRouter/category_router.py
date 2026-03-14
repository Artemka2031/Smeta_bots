from html import escape

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from Bot.Keyboards.Operations.category import (
    ChooseCategoryCallback,
    ChooseChapterCallback,
    ChooseSubCategoryCallback,
    category_choose_kb,
    chapters_choose_kb,
    subcategory_choose_kb,
)
from Bot.Routers.AddExpense.expense_state_class import Expense
from Bot.create_bot import ProjectBot


def create_category_router(bot: ProjectBot):
    category_router = Router()

    async def get_sheet_columns(state: FSMContext):
        data = await state.get_data()
        return data, data.get("column_b_values"), data.get("column_c_values")

    async def get_cached_chapters(state: FSMContext):
        data, codes, names = await get_sheet_columns(state)
        chapters = data.get("chapters")
        if not chapters:
            chapters = bot.google_sheets.get_chapters(codes, names)
            await state.update_data(chapters=chapters)
        return data, codes, names, chapters

    async def reset_chapter_selection(state: FSMContext):
        await state.update_data(
            chapter_code=None,
            chapter_name=None,
            categories=None,
            category_code=None,
            category_name=None,
            subcategories=None,
            subcategory_code=None,
            subcategory_name=None,
        )

    async def reset_category_selection(state: FSMContext):
        await state.update_data(
            categories=None,
            category_code=None,
            category_name=None,
            subcategories=None,
            subcategory_code=None,
            subcategory_name=None,
        )

    def safe_text(value: str) -> str:
        return escape(value or "")

    @category_router.callback_query(Expense.chapter_code, ChooseChapterCallback.filter(F.back == False))
    async def set_chapter(query: CallbackQuery, callback_data: ChooseChapterCallback, state: FSMContext):
        await query.answer()

        chapter_code = callback_data.chapter_code
        await reset_category_selection(state)

        data, codes, names = await get_sheet_columns(state)
        chapter_name = bot.google_sheets.get_chapter_name(chapter_code, codes, names)
        categories = bot.google_sheets.get_categories(chapter_code, codes, names)

        await state.update_data(
            chapter_code=chapter_code,
            chapter_name=chapter_name,
            categories=categories,
        )

        try:
            await query.message.edit_text(
                text=f"📖 Раздел: <b>{safe_text(chapter_name)}</b>\nВыберите категорию: ➡️",
                reply_markup=category_choose_kb(categories),
            )
        except Exception as exc:
            bot.logger.warning(f"Не удалось обновить сообщение выбора категории: {exc}")

        await state.set_state(Expense.category_code)

    @category_router.callback_query(Expense.category_code, ChooseCategoryCallback.filter(F.back == True))
    async def back_to_chapters(query: CallbackQuery, state: FSMContext):
        await query.answer()

        await reset_chapter_selection(state)
        _, _, _, chapters = await get_cached_chapters(state)

        try:
            await query.message.edit_text(
                text="Выберите раздел: 📖",
                reply_markup=chapters_choose_kb(chapters),
            )
        except Exception as exc:
            bot.logger.warning(f"Не удалось вернуться к выбору раздела: {exc}")

        await state.set_state(Expense.chapter_code)

    @category_router.callback_query(Expense.category_code, ChooseCategoryCallback.filter(F.back == False))
    async def set_category(query: CallbackQuery, callback_data: ChooseCategoryCallback, state: FSMContext):
        await query.answer()

        data, codes, names = await get_sheet_columns(state)
        chapter_code = data["chapter_code"]
        chapter_name = data.get("chapter_name", "Неизвестный раздел")
        category_code = callback_data.category_code

        if data.get("category_code") != category_code:
            await state.update_data(
                subcategories=None,
                subcategory_code=None,
                subcategory_name=None,
            )

        category_name = bot.google_sheets.get_category_name(chapter_code, category_code, codes, names)
        subcategories = bot.google_sheets.get_subcategories(chapter_code, category_code, codes, names)

        await state.update_data(
            category_code=category_code,
            category_name=category_name,
            subcategories=subcategories,
        )

        if subcategories:
            try:
                await query.message.edit_text(
                    text=(
                        f"📖 Раздел: <b>{safe_text(chapter_name)}</b>\n"
                        f"📋 Категория: <b>{safe_text(category_name)}</b>\n"
                        f"Выберите подкатегорию: ➡️"
                    ),
                    reply_markup=subcategory_choose_kb(subcategories),
                )
            except Exception as exc:
                bot.logger.warning(f"Не удалось показать подкатегории: {exc}")
            await state.set_state(Expense.subcategory_code)
            return

        try:
            await query.message.edit_text(
                text=(
                    f"📖 Раздел: <b>{safe_text(chapter_name)}</b>\n"
                    f"📋 Категория: <b>{safe_text(category_name)}</b>"
                ),
            )
            amount_message = await bot.send_message(
                chat_id=query.message.chat.id,
                text="Введите сумму расхода: 💰",
            )
        except Exception as exc:
            bot.logger.warning(f"Не удалось перейти к вводу суммы расхода: {exc}")
            return

        await state.update_data(amount_message_id=amount_message.message_id)
        await state.set_state(Expense.amount)

    @category_router.callback_query(Expense.subcategory_code, ChooseSubCategoryCallback.filter(F.back == True))
    async def back_to_category(query: CallbackQuery, state: FSMContext):
        await query.answer()

        data, codes, names = await get_sheet_columns(state)
        chapter_code = data["chapter_code"]
        chapter_name = data.get("chapter_name", "Неизвестный раздел")
        categories = bot.google_sheets.get_categories(chapter_code, codes, names)

        await state.update_data(
            categories=categories,
            category_code=None,
            category_name=None,
            subcategories=None,
            subcategory_code=None,
            subcategory_name=None,
        )

        try:
            await query.message.edit_text(
                text=f"📖 Раздел: <b>{safe_text(chapter_name)}</b>\nВыберите категорию: ➡️",
                reply_markup=category_choose_kb(categories),
            )
        except Exception as exc:
            bot.logger.warning(f"Не удалось вернуться к выбору категории: {exc}")

        await state.set_state(Expense.category_code)

    @category_router.callback_query(Expense.subcategory_code, ChooseSubCategoryCallback.filter(F.back == False))
    async def set_subcategory(query: CallbackQuery, callback_data: ChooseSubCategoryCallback, state: FSMContext):
        await query.answer()

        data, codes, names = await get_sheet_columns(state)
        chapter_code = data["chapter_code"]
        chapter_name = data.get("chapter_name", "Неизвестный раздел")
        category_code = data["category_code"]
        category_name = data.get("category_name", "Неизвестная категория")
        subcategory_code = callback_data.subcategory_code

        subcategory_name = bot.google_sheets.get_subcategory_name(
            chapter_code,
            category_code,
            subcategory_code,
            codes,
            names,
        )

        await state.update_data(
            subcategory_code=subcategory_code,
            subcategory_name=subcategory_name,
        )

        try:
            await query.message.edit_text(
                text=(
                    f"📖 Раздел: <b>{safe_text(chapter_name)}</b>\n"
                    f"📋 Категория: <b>{safe_text(category_name)}</b>\n"
                    f"📌 Подкатегория: <b>{safe_text(subcategory_name)}</b>"
                ),
            )
            amount_message = await bot.send_message(
                chat_id=query.message.chat.id,
                text="Введите сумму расхода: 💰",
            )
        except Exception as exc:
            bot.logger.warning(f"Не удалось перейти к вводу суммы после выбора подкатегории: {exc}")
            return

        await state.update_data(amount_message_id=amount_message.message_id)
        await state.set_state(Expense.amount)

    return category_router
