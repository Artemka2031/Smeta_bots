from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from Bot.Keyboards.Operations.category import ChooseChapterCallback, chapters_choose_kb, ChooseCategoryCallback, \
    category_choose_kb, subcategory_choose_kb, ChooseSubCategoryCallback
from Bot.Routers.AddExpense.expense_state_class import Expense
from Bot.create_bot import ProjectBot


def create_category_router(bot: ProjectBot):
    category_router = Router()

    @category_router.callback_query(Expense.chapter_code, ChooseChapterCallback.filter())
    async def set_chapter(query: CallbackQuery, callback_data: ChooseChapterCallback, state: FSMContext):
        await query.answer()

        chapter_code = callback_data.chapter_code
        await state.update_data(chapter_code=chapter_code)
        chapter_name = await bot.google_sheets.get_chapter_name(chapter_code)

        categories = await bot.google_sheets.get_categories(chapter_code)

        try:
            await query.message.edit_text(text=f'Выбран раздел "{chapter_name}". \nВыберите категорию:',
                                          reply_markup=category_choose_kb(categories))
        except:
            pass

        await state.set_state(Expense.category_code)

    @category_router.callback_query(Expense.category_code, ChooseCategoryCallback.filter(F.back == True))
    async def back_to_chapters(query: CallbackQuery, state: FSMContext):
        await query.answer()

        chapters = await bot.google_sheets.get_chapters()
        await query.message.edit_text(text="Выберите раздел:", reply_markup=chapters_choose_kb(chapters))
        await state.set_state(Expense.chapter_code)

    @category_router.callback_query(Expense.category_code, ChooseCategoryCallback.filter(F.back == False))
    async def set_category(query: CallbackQuery, callback_data: ChooseCategoryCallback, state: FSMContext):
        await query.answer()

        chapter_code = (await state.get_data())["chapter_code"]
        category_code = callback_data.category_code
        category_name = await bot.google_sheets.get_category_name(chapter_code, callback_data.category_code)

        # Обновляем состояние с выбранной категорией
        await state.update_data(category_code=category_code)

        # Проверяем, есть ли подкатегории у выбранной категории
        subcategories = await bot.google_sheets.get_subcategories(chapter_code, category_code)

        if subcategories:
            # Если есть подкатегории, переходим к выбору подкатегории
            await query.message.edit_text(f"Выбрана категория '{category_name}'. \nВыберите подкатегорию:",
                                          reply_markup=subcategory_choose_kb(subcategories))
            await state.set_state(Expense.subcategory_code)
        else:
            # Если подкатегорий нет, переходим к вводу суммы расхода
            await query.message.edit_text(f"Выбрана категория '{category_name}'.")
            amount_message = await bot.send_message(chat_id=query.message.chat.id, text="Введите сумму расхода:")
            await state.update_data(amount_message_id=amount_message.message_id)
            await state.set_state(Expense.amount)

    @category_router.callback_query(Expense.subcategory_code, ChooseSubCategoryCallback.filter(F.back == True))
    async def back_to_category(query: CallbackQuery, state: FSMContext):
        await query.answer()

        # Получаем код текущего раздела из состояния
        data = await state.get_data()
        chapter_code = data['chapter_code']

        # Получаем список категорий из Google Sheets для данного раздела
        categories = await bot.google_sheets.get_categories(chapter_code)

        await query.message.edit_text(text="Выберите категорию:", reply_markup=category_choose_kb(categories))
        await state.set_state(Expense.category_code)

    @category_router.callback_query(Expense.subcategory_code, ChooseSubCategoryCallback.filter(F.back == False))
    async def set_subcategory(query: CallbackQuery, callback_data: ChooseSubCategoryCallback, state: FSMContext):
        await query.answer()

        data = await state.get_data()
        chapter_code = data['chapter_code']
        category_code = data['category_code']

        subcategory_code = callback_data.subcategory_code
        subcategory_name = await bot.google_sheets.get_subcategory_name(chapter_code, category_code, subcategory_code)

        # Обновляем состояние с выбранной подкатегорией
        await state.update_data(subcategory_code=subcategory_code)

        await query.message.edit_text(f"Выбрана подкатегория '{subcategory_name}'.")
        amount_message = await bot.send_message(chat_id=query.message.chat.id, text="Введите сумму расхода:")
        await state.update_data(amount_message_id=amount_message.message_id)
        await state.set_state(Expense.amount)

    @category_router.callback_query(Expense.category_code, ChooseCategoryCallback.filter(F.back == True))
    async def back_to_chapters(query: CallbackQuery, state: FSMContext):
        await query.answer()

        # Получаем список разделов из Google Sheets
        chapters = await bot.google_sheets.get_chapters()
        await query.message.edit_text(text="Выберите раздел:", reply_markup=chapters_choose_kb(chapters))
        await state.set_state(Expense.chapter_code)

    return category_router
