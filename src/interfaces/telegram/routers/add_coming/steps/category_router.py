from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from src.interfaces.telegram.keyboards.operations.category import ChooseChapterCallback, chapters_choose_kb, ChooseCategoryCallback, \
    category_choose_kb
from src.interfaces.telegram.routers.add_coming.coming_state_class import Coming
from src.interfaces.telegram.project_bot import ProjectBot
from src.application.use_cases import GetProjectCatalog
from src.interfaces.telegram.flow_utils import send_next_operation_prompt


def create_category_router(bot: ProjectBot):
    category_router = Router()
    project_catalog = GetProjectCatalog(bot.sheets_gateway)

    @category_router.callback_query(Coming.chapter_code, ChooseChapterCallback.filter(F.back == True))
    async def cancel_coming_adding(query: CallbackQuery, state: FSMContext):
        await query.answer()

        await state.clear()

        try:
            await query.message.edit_text("Добавление прихода отменено.")
        except Exception as exc:
            bot.logger.warning(f"Не удалось обновить сообщение отмены прихода: {exc}")

        await send_next_operation_prompt(bot, query.message.chat.id)

    @category_router.callback_query(Coming.chapter_code, ChooseChapterCallback.filter(F.back == False))
    async def set_chapter(query: CallbackQuery, callback_data: ChooseChapterCallback, state: FSMContext):
        await query.answer()

        chapter_code = callback_data.chapter_code
        await state.update_data(chapter_code=chapter_code)

        categories = await project_catalog.get_categories(chapter_code)

        try:
            await query.message.edit_text(text=f'Выберите кошелёк прихода:',
                                          reply_markup=category_choose_kb(categories))
        except Exception as exc:
            bot.logger.warning(f"Не удалось показать категории прихода: {exc}")

        await state.set_state(Coming.coming_code)

    @category_router.callback_query(Coming.coming_code, ChooseCategoryCallback.filter(F.back == True))
    async def back_to_chapters(query: CallbackQuery, state: FSMContext):
        await query.answer()

        chapters = await project_catalog.get_coming_chapters()
        await query.message.edit_text(text="Выберите раздел:", reply_markup=chapters_choose_kb(chapters))
        await state.set_state(Coming.chapter_code)

    @category_router.callback_query(Coming.coming_code, ChooseCategoryCallback.filter(F.back == False))
    async def set_category(query: CallbackQuery, callback_data: ChooseCategoryCallback, state: FSMContext):
        await query.answer()

        chapter_code = (await state.get_data())["chapter_code"]
        coming_code = callback_data.category_code
        category_name = await project_catalog.get_category_name(chapter_code, callback_data.category_code)

        # Обновляем состояние с выбранной категорией
        await state.update_data(coming_code=coming_code)

        await query.message.edit_text(f"Выбрана категория '{category_name}'.")
        amount_message = await bot.send_message(chat_id=query.message.chat.id, text="Введите сумму прихода:")
        await state.update_data(amount_message_id=amount_message.message_id)
        await state.set_state(Coming.amount)

    return category_router
