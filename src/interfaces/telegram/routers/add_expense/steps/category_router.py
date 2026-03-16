from html import escape

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from src.interfaces.telegram.keyboards.operations.category import (
    ChooseCategoryCallback,
    ChooseChapterCallback,
    ChooseSubCategoryCallback,
    category_choose_kb,
    chapters_choose_kb,
    subcategory_choose_kb,
)
from src.interfaces.telegram.routers.add_expense.expense_state_class import Expense
from src.interfaces.telegram.project_bot import ProjectBot
from src.application.use_cases import GetProjectCatalog


def create_category_router(bot: ProjectBot):
    category_router = Router()
    project_catalog = GetProjectCatalog(bot.sheets_gateway)

    async def reset_chapter_selection(state: FSMContext):
        await state.update_data(
            chapter_code=None,
            chapter_name=None,
            category_code=None,
            category_name=None,
            subcategory_code=None,
            subcategory_name=None,
        )

    async def reset_category_selection(state: FSMContext):
        await state.update_data(
            category_code=None,
            category_name=None,
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

        data = await state.get_data()
        chapter_name = await project_catalog.get_chapter_name(chapter_code)
        await state.update_data(
            chapter_code=chapter_code,
            chapter_name=chapter_name,
        )
        categories = await project_catalog.get_categories(chapter_code)

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
        chapters = await project_catalog.get_expense_chapters()

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

        data = await state.get_data()
        chapter_code = data["chapter_code"]
        chapter_name = data.get("chapter_name", "Неизвестный раздел")
        category_code = callback_data.category_code

        if data.get("category_code") != category_code:
            await state.update_data(
                subcategory_code=None,
                subcategory_name=None,
            )

        category_name = await project_catalog.get_category_name(chapter_code, category_code)
        subcategories = await project_catalog.get_subcategories(chapter_code, category_code)

        await state.update_data(
            category_code=category_code,
            category_name=category_name,
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

        data = await state.get_data()
        chapter_code = data["chapter_code"]
        chapter_name = data.get("chapter_name", "Неизвестный раздел")
        await state.update_data(
            category_code=None,
            category_name=None,
            subcategory_code=None,
            subcategory_name=None,
        )
        categories = await project_catalog.get_categories(chapter_code)

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

        data = await state.get_data()
        chapter_code = data["chapter_code"]
        chapter_name = data.get("chapter_name", "Неизвестный раздел")
        category_code = data["category_code"]
        category_name = data.get("category_name", "Неизвестная категория")
        subcategory_code = callback_data.subcategory_code

        subcategory_name = await project_catalog.get_subcategory_name(
            chapter_code,
            category_code,
            subcategory_code,
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
