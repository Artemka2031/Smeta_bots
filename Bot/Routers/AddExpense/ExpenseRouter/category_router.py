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

        # Получаем chapter_code из callback и сохраняем в состояние
        chapter_code = callback_data.chapter_code
        await state.update_data(chapter_code=chapter_code)

        # Загружаем данные из состояния
        data = await state.get_data()
        chapters = data.get('chapters')

        chapter_code_list = data.get('column_b_values')  # Коды разделов из состояния
        chapter_name_list = data.get('column_c_values')  # Названия разделов из состояния

        # Если данных о главах нет, загружаем их из Google Sheets и сохраняем
        if not chapters:
            chapters = bot.google_sheets.get_chapters(chapter_code_list, chapter_name_list)
            await state.update_data(chapters=chapters)

        chapter_name = bot.google_sheets.get_chapter_name(chapter_code, chapter_code_list, chapter_name_list)

        # Загружаем категории для выбранного раздела
        categories = bot.google_sheets.get_categories(chapter_code, chapter_code_list, chapter_name_list)

        # Отправляем сообщение с выбором категории
        try:
            await query.message.edit_text(text=f'Выбран раздел "{chapter_name}". \nВыберите категорию:',
                                          reply_markup=category_choose_kb(categories))
        except:
            pass

        await state.set_state(Expense.category_code)

    @category_router.callback_query(Expense.category_code, ChooseCategoryCallback.filter(F.back == True))
    async def back_to_chapters(query: CallbackQuery, state: FSMContext):
        await query.answer()

        # Загружаем данные из состояния
        data = await state.get_data()
        chapters = data.get('chapters')

        # Если данных о главах нет, загружаем их из Google Sheets
        if not chapters:
            chapter_code_list = data.get('column_b_values')  # Коды разделов из состояния
            chapter_name_list = data.get('column_c_values')  # Названия разделов из состояния
            chapters = bot.google_sheets.get_chapters(chapter_code_list, chapter_name_list)
            await state.update_data(chapters=chapters)

        await query.message.edit_text(text="Выберите раздел:", reply_markup=chapters_choose_kb(chapters))
        await state.set_state(Expense.chapter_code)

    @category_router.callback_query(Expense.category_code, ChooseCategoryCallback.filter(F.back == False))
    async def set_category(query: CallbackQuery, callback_data: ChooseCategoryCallback, state: FSMContext):
        await query.answer()

        # Загружаем данные из состояния
        data = await state.get_data()
        chapter_code = data['chapter_code']
        category_code = callback_data.category_code

        # Сохраняем код категории в состоянии
        await state.update_data(category_code=category_code)

        # Получаем коды и имена разделов из состояния
        chapter_code_list = data.get('column_b_values')  # Коды разделов
        chapter_name_list = data.get('column_c_values')  # Названия разделов

        # Получаем имя категории из состояния или извлекаем его из загруженных данных
        category_name = data.get("category_name")
        if not category_name:
            category_name = bot.google_sheets.get_category_name(chapter_code, category_code, chapter_code_list,
                                                                chapter_name_list)
            await state.update_data(category_name=category_name)

        # Получаем подкатегории для выбранной категории из состояния или извлекаем из загруженных данных
        subcategories = data.get('subcategories')
        if not subcategories:
            subcategories = bot.google_sheets.get_subcategories(chapter_code, category_code, chapter_code_list,
                                                                chapter_name_list)
            await state.update_data(subcategories=subcategories)

        # Если есть подкатегории, предлагаем их выбор
        if subcategories:
            await query.message.edit_text(
                f"Выбрана категория '{category_name}'. \nВыберите подкатегорию:",
                reply_markup=subcategory_choose_kb(subcategories)
            )
            await state.set_state(Expense.subcategory_code)
        else:
            # Если подкатегорий нет, переходим к вводу суммы
            await query.message.edit_text(f"Выбрана категория '{category_name}'.")
            amount_message = await bot.send_message(chat_id=query.message.chat.id, text="Введите сумму расхода:")
            await state.update_data(amount_message_id=amount_message.message_id)
            await state.set_state(Expense.amount)

    @category_router.callback_query(Expense.subcategory_code, ChooseSubCategoryCallback.filter(F.back == True))
    async def back_to_category(query: CallbackQuery, state: FSMContext):
        await query.answer()

        # Загружаем данные из состояния
        data = await state.get_data()
        chapter_code = data['chapter_code']

        # Получаем категории из состояния или загружаем из Google Sheets
        categories = data.get('categories')
        if not categories:
            # Получаем коды и имена разделов из состояния
            chapter_code_list = data.get('column_b_values')  # Коды разделов
            chapter_name_list = data.get('column_c_values')  # Названия разделов

            # Загружаем категории с использованием данных из состояния
            categories = bot.google_sheets.get_categories(chapter_code, chapter_code_list, chapter_name_list)
            await state.update_data(categories=categories)

        await query.message.edit_text(text="Выберите категорию:", reply_markup=category_choose_kb(categories))
        await state.set_state(Expense.category_code)

    @category_router.callback_query(Expense.subcategory_code, ChooseSubCategoryCallback.filter(F.back == False))
    async def set_subcategory(query: CallbackQuery, callback_data: ChooseSubCategoryCallback, state: FSMContext):
        await query.answer()

        # Загружаем данные из состояния
        data = await state.get_data()
        chapter_code = data['chapter_code']
        category_code = data['category_code']

        # Получаем коды и имена разделов из состояния
        chapter_code_list = data.get('column_b_values')  # Коды разделов
        chapter_name_list = data.get('column_c_values')  # Названия разделов

        # Получаем название подкатегории с использованием данных из состояния
        subcategory_code = callback_data.subcategory_code
        subcategory_name = bot.google_sheets.get_subcategory_name(chapter_code, category_code, subcategory_code,
                                                                  chapter_code_list, chapter_name_list)

        # Обновляем состояние с кодом подкатегории
        await state.update_data(subcategory_code=subcategory_code)

        # Переход к вводу суммы
        await query.message.edit_text(f"Выбрана подкатегория '{subcategory_name}'.")
        amount_message = await bot.send_message(chat_id=query.message.chat.id, text="Введите сумму расхода:")
        await state.update_data(amount_message_id=amount_message.message_id)
        await state.set_state(Expense.amount)

    @category_router.callback_query(Expense.category_code, ChooseCategoryCallback.filter(F.back == True))
    async def back_to_chapters(query: CallbackQuery, state: FSMContext):
        await query.answer()

        # Загружаем данные из состояния
        data = await state.get_data()
        chapters = data.get('chapters')

        # Если данных о главах нет, загружаем их из Google Sheets
        if not chapters:
            # Получаем коды и имена разделов из состояния
            chapter_code_list = data.get('column_b_values')  # Коды разделов
            chapter_name_list = data.get('column_c_values')  # Названия разделов

            # Загружаем разделы (главы) с использованием данных из состояния
            chapters = bot.google_sheets.get_chapters(chapter_code_list, chapter_name_list)
            await state.update_data(chapters=chapters)

        await query.message.edit_text(text="Выберите раздел:", reply_markup=chapters_choose_kb(chapters))
        await state.set_state(Expense.chapter_code)

    return category_router
