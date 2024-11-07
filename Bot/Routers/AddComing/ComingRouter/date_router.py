from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from Bot.Filters.check_date import CheckDate
from Bot.Keyboards.Operations.category import TodayCallback, chapters_choose_kb
from Bot.Keyboards.Operations.wallet import create_wallet_keyboard
from Bot.Routers.AddComing.coming_state_class import Coming
from Bot.create_bot import ProjectBot


def create_date_router(bot: ProjectBot):
    date_router = Router()

    @date_router.callback_query(Coming.date, TodayCallback.filter())
    async def change_date(query: CallbackQuery, callback_data: TodayCallback, state: FSMContext):
        await state.set_state(Coming.date)
        chat_id = query.message.chat.id

        try:
            extra_messages = (await state.get_data())["extra_messages"]

            for message_id in extra_messages:
                await bot.delete_message(chat_id=chat_id, message_id=message_id)
            await state.update_data(extra_messages=None)
        except:
            pass

        date = callback_data.today
        await query.message.edit_text(f"Выбрана дата: {date}", reply_markup=None)
        await state.update_data(date=date)

        coming = bot.google_sheets.get_coming()

        coming_message = await query.message.edit_text(text=f"Выберите категорию прихода:",
                                                       reply_markup=chapters_choose_kb(coming))
        await state.update_data(coming_message_id=coming_message.message_id)
        await state.set_state(Coming.chapter_code)


    @date_router.message(Coming.date, CheckDate(F.text))
    async def invalid_date_format(message: Message, state: FSMContext):
        await message.delete()

        try:
            extra_messages = (await state.get_data())["extra_messages"]
        except:
            incorrect_date_message = await bot.send_message(
                chat_id=message.chat.id,
                text="Дата должна быть в формате дд.мм.гггг и не позднее сегодняшнего дня. Повторите:")
            incorrect_date_message_id = incorrect_date_message.message_id
            await state.update_data(extra_messages=[incorrect_date_message_id])

        await state.set_state(Coming.date)

    @date_router.message(Coming.date)
    async def set_date_text(message: Message, state: FSMContext):
        date = message.text
        chat_id = message.chat.id

        try:
            extra_messages = (await state.get_data())["extra_messages"]

            for message_id in extra_messages:
                await bot.delete_message(chat_id=chat_id, message_id=message_id)
            await state.update_data(extra_messages=None)
        except:
            pass

        await message.delete()

        date_message_id = (await state.get_data())["date_message_id"]
        await bot.edit_message_text(chat_id=chat_id, message_id=date_message_id,
                                    text=f"Выбрана дата: {date}", reply_markup=None)
        await state.update_data(date=date)

        coming = bot.google_sheets.get_coming()

        coming_message = await message.edit_text(text=f"Выберите категорию прихода:",
                                                 reply_markup=chapters_choose_kb(coming))
        await state.update_data(coming_message_id=coming_message.message_id)
        await state.set_state(Coming.chapter_code)

    return date_router
