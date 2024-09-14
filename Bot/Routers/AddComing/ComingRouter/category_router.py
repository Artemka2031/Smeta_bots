from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from Bot.Keyboards.Operations.category import ChooseChapterCallback, chapters_choose_kb, ChooseCategoryCallback, \
    category_choose_kb, subcategory_choose_kb, ChooseSubCategoryCallback
from Bot.Routers.AddComing.coming_state_class import Coming
from Bot.create_bot import ProjectBot


def create_category_router(bot: ProjectBot):
    category_router = Router()

    @category_router.callback_query(Coming.chapter_code, ChooseChapterCallback.filter())
    async def set_chapter(query: CallbackQuery, callback_data: ChooseChapterCallback, state: FSMContext):
        await query.answer()

        chapter_code = callback_data.chapter_code
        await state.update_data(chapter_code=chapter_code)

        categories = bot.google_sheets.get_categories(chapter_code)

        try:
            await query.message.edit_text(text=f'Выберите кошелёк прихода:',
                                          reply_markup=category_choose_kb(categories))
        except:
            pass

        await state.set_state(Coming.coming_code)

    @category_router.callback_query(Coming.chapter_code, ChooseCategoryCallback.filter(F.back == True))
    async def back_to_chapters(query: CallbackQuery, state: FSMContext):
        await query.answer()

        chapters = bot.google_sheets.get_chapters()
        await query.message.edit_text(text="Выберите раздел:", reply_markup=chapters_choose_kb(chapters))
        await state.set_state(Coming.chapter_code)

    @category_router.callback_query(Coming.coming_code, ChooseCategoryCallback.filter(F.back == False))
    async def set_category(query: CallbackQuery, callback_data: ChooseCategoryCallback, state: FSMContext):
        await query.answer()

        chapter_code = (await state.get_data())["chapter_code"]
        coming_code = callback_data.category_code
        category_name = bot.google_sheets.get_category_name(chapter_code, callback_data.category_code)

        # Обновляем состояние с выбранной категорией
        await state.update_data(coming_code=coming_code)

        await query.message.edit_text(f"Выбрана категория '{category_name}'.")
        amount_message = await bot.send_message(chat_id=query.message.chat.id, text="Введите сумму прихода:")
        await state.update_data(amount_message_id=amount_message.message_id)
        await state.set_state(Coming.amount)

    return category_router
