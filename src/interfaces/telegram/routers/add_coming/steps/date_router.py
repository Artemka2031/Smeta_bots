from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from src.interfaces.telegram.filters.check_date import CheckDate
from src.interfaces.telegram.keyboards.operations.category import TodayCallback, chapters_choose_kb
from src.interfaces.telegram.routers.add_coming.coming_state_class import Coming
from src.interfaces.telegram.project_bot import ProjectBot
from src.application.use_cases import GetProjectCatalog
from src.interfaces.telegram.state_utils import clear_extra_messages, ensure_extra_message


def create_date_router(bot: ProjectBot):
    date_router = Router()
    project_catalog = GetProjectCatalog(bot.sheets_gateway)

    @date_router.callback_query(Coming.date, TodayCallback.filter())
    async def change_date(query: CallbackQuery, callback_data: TodayCallback, state: FSMContext):
        await state.set_state(Coming.date)
        chat_id = query.message.chat.id
        await clear_extra_messages(bot, state, chat_id, bot.logger)

        date = callback_data.today
        await query.message.edit_text(f"Выбрана дата: {date}", reply_markup=None)
        await state.update_data(date=date)

        coming = await project_catalog.get_coming_chapters()

        coming_message = await query.message.edit_text(text=f"Выберите категорию прихода:",
                                                       reply_markup=chapters_choose_kb(coming))
        await state.update_data(coming_message_id=coming_message.message_id)
        await state.set_state(Coming.chapter_code)

    @date_router.message(Coming.date, CheckDate(F.text))
    async def invalid_date_format(message: Message, state: FSMContext):
        await message.delete()
        await ensure_extra_message(
            bot,
            state,
            message.chat.id,
            "Дата должна быть в формате дд.мм.гг и не позднее сегодняшнего дня. Повторите:",
        )

        await state.set_state(Coming.date)

    @date_router.message(Coming.date)
    async def set_date_text(message: Message, state: FSMContext):
        date = message.text
        chat_id = message.chat.id
        await clear_extra_messages(bot, state, chat_id, bot.logger)

        await message.delete()

        date_message_id = (await state.get_data())["date_message_id"]
        await bot.edit_message_text(chat_id=chat_id, message_id=date_message_id,
                                    text=f"Выбрана дата: {date}", reply_markup=None)
        await state.update_data(date=date)

        coming = await project_catalog.get_coming_chapters()

        coming_message = await bot.send_message(chat_id=chat_id,
                                                text="Выберите категорию прихода:",
                                                reply_markup=chapters_choose_kb(coming))
        await state.update_data(coming_message_id=coming_message.message_id)
        await state.set_state(Coming.chapter_code)

    return date_router
