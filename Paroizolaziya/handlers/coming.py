import datetime
import logging
from loguru import logger
from aiogram import types
from aiogram.dispatcher import filters, Dispatcher, FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils.callback_data import CallbackData
import re

from Paroizolaziya.create_bot import bot
from Paroizolaziya.keyBoards import generalKB, comingKB, startKB


class FSMcoming(StatesGroup):
    names = ['date', 'comming', 'coming_ammount', "comming_comment"]
    date = State()
    comming = State()
    coming_ammount = State()
    comming_comment = State()


start_message_id = 10000000000000000


async def start_comming_adding(message_from: types.Message, state: FSMContext) -> None:
    date_kb = generalKB.date_kb()

    global start_message_id
    start_message_id = message_from.message_id

    await message_from.answer('Введите дату: 📅', reply_markup=date_kb)
    await FSMcoming.date.set()


async def load_date(callback_query: types.CallbackQuery, state: FSMContext):

    chat_id = callback_query.message.chat.id
    today = datetime.datetime.today()

    async with state.proxy() as data:
        data['date'] = today.strftime("%d.%m.%Y")
    await FSMcoming.next()

    await bot.answer_callback_query(callback_query.id)
    await callback_query.message.edit_text(f"Выбрана дата: 🗓️ {today.strftime('%d.%m.%Y')}")

    types = await bot.transaction.get_types_of_comming()
    comming_kb = comingKB.create_comming_types_kb(types)

    await bot.send_message(chat_id=chat_id, text="Выберите тип прихода: 💰", reply_markup=comming_kb)


async def load_date_text(message: types.Message, state: FSMContext):
    chat_id = message.chat.id
    message_id = message.message_id

    await state.update_data(date=message.text)
    await FSMcoming.next()
    await bot.delete_message(chat_id, message_id)
    await bot.edit_message_text(chat_id=chat_id, message_id=message_id - 1, text=f"Выбрана дата: 🗓️ {message.text}", reply_markup=None)

    types = await bot.transaction.get_types_of_comming()
    comming_kb = comingKB.create_comming_types_kb(types)

    await bot.send_message(chat_id=chat_id, text="Выберите тип прихода: 💰", reply_markup=comming_kb)


async def load_type(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['comming'] = call.data
    await FSMcoming.next()

    await call.message.edit_text(f"Тип прихода: 💰 {call.data}")
    await bot.send_message(call.message.chat.id, "Введите сумму: 💲")


async def date_invalid(message: types.Message):
    chat_id = message.chat.id
    message_id = message.message_id

    await bot.delete_message(chat_id, message_id - 1)
    await bot.delete_message(chat_id, message_id)
    return await bot.send_message(chat_id=chat_id, text="Выберите дату: 🗓️/nОна должна быть в формате дд.мм.гггг (Например16.05.2023)", reply_markup=generalKB.date_kb())


async def ammount_invalid(message: types.Message):
    return await message.reply("Сумма должна быть числом. 🧮")

edit_or_delete_coming = CallbackData(
    "edit_or_delete", "action", "expence_id", "message_id")


async def load_coming_amount(message_from: types.Message, state: FSMContext):
    chat_id: str = str(message_from.chat.id)

    async with state.proxy() as data:
        data['coming_ammount'] = message_from.text
    await FSMcoming.next()

    await bot.send_message(chat_id, text="Введите комментарий: 💬")

    
    
async def load_coming_comment(message_from: types.Message, state: FSMContext):
    user_id: str = str(message_from.chat.id)
    message_id = message_from.message_id

    async with state.proxy() as data:
        data['comming_comment'] = message_from.text
        print(data)
        await bot.transaction.add_coming(data, FSMcoming.names)
    await state.finish()

    check = await bot.transaction.get_last_coming()
    start_kb = startKB.create_start_kb()
    
    try:
        if check:

            id = check[0]
            date = check[1]
            wallet = check[2]
            ammount = check[3]
            comment = check[5]

            text = f'Приход:\nДата: 📅 {date}\nОт: 💼 <b>{wallet}</b>\nСумма прихода: 💰 {ammount}\nКомментарий: 💬 {comment}'
            edit_or_delete_kb = generalKB.edit_or_delete_coming_kb(
                id, message_id + 1, edit_or_delete_coming)
            await bot.send_message(user_id, text, parse_mode="HTML", reply_markup=edit_or_delete_kb)

            message = "Выберите дальнейшую операцию 🔄"
            await bot.send_message(user_id, message, parse_mode="HTML", reply_markup=start_kb)

            for i in range(0, message_id - start_message_id + 1):
                try:
                    await bot.delete_message(message_from.chat.id, message_id - i)
                except: i += 1

    except Exception as send_error:
        logger.debug(f"{send_error.message}: Truble id: {user_id}")
        return


async def delete_coming(call: types.CallbackQuery, callback_data: dict):
    await bot.answer_callback_query(call.id)
    chat_id = call.message.chat.id
    message_id = callback_data.get('message_id')
    expence_id = callback_data.get('expence_id')

    await bot.transaction.delete_coming(expence_id)
    text = call.message.text + "\n\n***Удалено***"
    await bot.edit_message_text(chat_id=chat_id, text=text, message_id=message_id, reply_markup="")


async def cancel_handler(message: types.Message, state: FSMContext):
    chat_id = message.chat.id
    current_state = await state.get_state()
    if current_state is None:
        return

    logging.info('Cancelling state %r', current_state)
    await state.finish()

    [await bot.delete_message(message.chat.id, message.message_id - i) for i in range(0, message.message_id - start_message_id + 1)]
    await bot.send_message(chat_id, 'Операция отменина. ❌', reply_markup=startKB.create_start_kb())


def register_handlers_admin(dp: Dispatcher):
    dp.register_message_handler(
        start_comming_adding, filters.Regexp(regexp=r"(Приход)"), state=None)
    dp.register_message_handler(
        cancel_handler, filters.Regexp(regexp=r"(Отмена приход)"), state='*')
    dp.register_message_handler(cancel_handler, state='*', commands='cancle')

    dp.register_callback_query_handler(
        load_date, lambda c: c.data == 'today', state=FSMcoming.date)
    dp.register_message_handler(
        date_invalid,
        lambda message: not (re.match(r'^\d{2}\.\d{2}\.\d{4}$', message.text)),
        state=FSMcoming.date)
    dp.register_message_handler(load_date_text, state=FSMcoming.date)

    dp.register_callback_query_handler(
        load_type, state=FSMcoming.comming)

    dp.register_message_handler(
        ammount_invalid, lambda message: not (re.match(r'^[\d,]+$', message.text)), state=FSMcoming.coming_ammount)
    dp.register_message_handler(
        load_coming_amount,  state=FSMcoming.coming_ammount)
    
    dp.register_message_handler(
        load_coming_comment,  state=FSMcoming.comming_comment)

    # dp.register_callback_query_handler(edit_expence, cd_edit_byid.filter())
    dp.register_callback_query_handler(
        delete_coming, edit_or_delete_coming.filter(action="Coming del"))
    # dp.register_callback_query_handler(
    #     edit, edit_or_delete.filter(action = "Edit"))
    # dp.register_callback_query_handler(
    #     back_to_edit, to_edit.filter(editable_value = "Назад"))
