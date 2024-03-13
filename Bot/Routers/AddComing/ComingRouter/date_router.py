from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.methods import EditMessageText, DeleteMessage
from aiogram.types import CallbackQuery, Message

from Database.Tables.ComingTables import ComingCategory
from Bot.Filters.check_date import CheckDate
from Bot.Keyboards.Operations.category import TodayCallback, category_choose_kb
from Bot.Routers.AddComing.coming_state_class import Coming

dateRouter = Router()


@dateRouter.callback_query(Coming.date, TodayCallback.filter())
async def change_date(query: CallbackQuery, callback_data: TodayCallback, state: FSMContext, bot: Bot):
    await state.set_state(Coming.date)
    chat_id = query.message.chat.id

    try:
        extra_messages = (await state.get_data())["extra_messages"]

        for message_id in extra_messages:
            try:
                await bot(DeleteMessage(chat_id=chat_id, message_id=message_id))
            except:
                pass
        await state.update_data(extra_messages=None)
    except:
        pass

    date = callback_data.today
    await query.message.edit_text(f"Выбрана дата: {date}", reply_markup=None)

    await state.update_data(date=date)

    category_message = await query.message.answer(text="Выберите категорию:", reply_markup=category_choose_kb(ComingCategory))
    await state.update_data(category_message_id=category_message.message_id)

    await state.set_state(Coming.category)


@dateRouter.message(Coming.date, CheckDate(F.text))
async def invalid_date_format(message: Message, state: FSMContext):
    await message.delete()

    try:
        extra_messages = (await state.get_data())["extra_messages"]
    except:
        incorrect_date_message = await message.answer(
            text="Дата должна быть от 2022 до 2030 и не позднее сегодняшнего дня. 📅 \nФормат: дд.мм.гг Повторите:")
        incorrect_date_message_id = incorrect_date_message.message_id
        await state.update_data(extra_messages=[incorrect_date_message_id])

    await state.set_state(Coming.date)


@dateRouter.message(Coming.date)
async def set_date_text(message: Message, state: FSMContext, bot: Bot):
    date = message.text
    chat_id = message.chat.id

    try:
        extra_messages = (await state.get_data())["extra_messages"]

        for message_id in extra_messages:
            try:
                await bot(DeleteMessage(chat_id=chat_id, message_id=message_id))
            except:
                pass
        await state.update_data(extra_messages=None)
    except:
        pass

    await message.delete()

    await state.update_data(date=date)

    date_message_id = (await state.get_data())["date_message_id"]
    await bot(EditMessageText(chat_id=chat_id, message_id=date_message_id,
                              text=f"Выбрана дата: {date}", reply_markup=None))
    category_message = await message.answer(text="Выберите категорию:", reply_markup=category_choose_kb(ComingCategory))
    await state.update_data(category_message_id=category_message.message_id)

    await state.set_state(Coming.category)
