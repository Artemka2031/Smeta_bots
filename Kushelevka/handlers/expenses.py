import datetime
import logging
import re
from loguru import logger
from aiogram import types
from aiogram.dispatcher import filters, Dispatcher, FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils.callback_data import CallbackData

from evropeysakaya.create_bot import bot
from evropeysakaya.keyBoards import expenceKB, generalKB, startKB


start_message_id = 10000000000000000


class FSMexpence(StatesGroup):
    names = ['date', 'wallet', 'type', 'ammount', 'comment']
    date = State()
    wallet = State()
    type = State()
    ammount = State()
    comment = State()


wallet_choose = CallbackData("wallet", "callback_data", "message_id")


async def start_expence_adding(message_from: types.Message, state: FSMContext) -> None:
    date_kb = generalKB.date_kb()

    global start_message_id
    start_message_id = message_from.message_id

    await message_from.answer('Введите дату: 📅', reply_markup=date_kb)
    await FSMexpence.date.set()


category_choose = CallbackData("expence", "callback_data", "message_id")
move = CallbackData("movement", "move", "message_id")
credititors_debt = CallbackData("debt", "creditor", "debt")


async def load_date(callback_query: types.CallbackQuery, state: FSMContext):

    chat_id = callback_query.message.chat.id
    message_id = callback_query.message.message_id

    today = datetime.datetime.today()

    async with state.proxy() as data:
        data['date'] = today.strftime("%d.%m.%Y")
    await FSMexpence.next()

    await bot.answer_callback_query(callback_query.id)
    await callback_query.message.edit_text(f"Выбрана дата: 🗓️ {today.strftime('%d.%m.%Y')}")

    wallets = await bot.transaction.get_wallets()
    wallets_kb = generalKB.create_wallets_kb(
        wallets, message_id + 1, wallet_choose)

    await bot.send_message(chat_id=chat_id, text="Выберите кошелёк: 💼", reply_markup=wallets_kb)


async def load_date_text(message: types.Message, state: FSMContext):
    chat_id = message.chat.id
    message_id = message.message_id

    await state.update_data(date=message.text)
    await FSMexpence.next()
    await bot.delete_message(chat_id, message_id)
    await bot.edit_message_text(chat_id=chat_id, message_id=message_id - 1, text=f"Выбрана дата: 🗓️ {message.text}", reply_markup=None)

    wallets = await bot.transaction.get_wallets()
    wallets_kb = generalKB.create_wallets_kb(
        wallets, message_id + 2, wallet_choose)

    await bot.send_message(chat_id=chat_id, text="Выберите кошелёк: 💼", reply_markup=wallets_kb)


async def date_invalid(message: types.Message):
    chat_id = message.chat.id
    message_id = message.message_id

    await bot.delete_message(chat_id, message_id - 1)
    await bot.delete_message(chat_id, message_id)
    return await bot.send_message(chat_id=chat_id, text="Выберите дату: 🗓️/nОна должна быть в формате дд.мм.гггг (Например16.05.2023)", reply_markup=generalKB.date_kb())


async def load_wallet(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    chat_id = call.message.chat.id

    if callback_data.get("callback_data") == (await bot.transaction.get_wallets())[0]:
        async with state.proxy() as data:
            data['wallet'] = callback_data.get("callback_data")
        await FSMexpence.next()

        await bot.answer_callback_query(call.id)
        await call.message.edit_text("Кошелёк: 💼 Проект")

        message_id = call.message.message_id + 1

        categories = await bot.transaction.get_categories_of_expences()
        categories_of_expence_kb = expenceKB.create_expence_categories_kb_without_debt(
            categories, message_id, category_choose)

        await bot.send_message(chat_id, text="Какая категория расхода? 📊", reply_markup=categories_of_expence_kb)

    elif callback_data.get("callback_data") == (await bot.transaction.get_wallets())[1]:
        message_id = callback_data.get("message_id")

        creditors = await bot.transaction.get_creditors()
        creditors_kb = generalKB.create_creditors_borrow_kb(
            creditors, message_id, move, credititors_debt)

        await call.message.edit_reply_markup(creditors_kb)

    else:
        message_id = callback_data.get("message_id")

        creditors = await bot.transaction.get_creditors()
        creditors_kb = generalKB.create_creditors_return_kb(
            creditors, message_id, move, credititors_debt)

        await call.message.edit_reply_markup(creditors_kb)


async def back_to_wallets(call: types.CallbackQuery, callback_data: dict):
    chat_id = call.message.chat.id
    message_id = callback_data.get("message_id")

    wallets = await bot.transaction.get_wallets()
    wallets_kb = generalKB.create_wallets_kb(
        wallets, message_id, wallet_choose)

    await call.message.edit_reply_markup(wallets_kb)


async def load_creditor(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    chat_id = call.message.chat.id

    # Если взяли в долг
    async with state.proxy() as data:
        creditor = callback_data.get("creditor")
        debt = callback_data.get("debt")

        wallet = [creditor, debt]

        data['wallet'] = wallet
    await FSMexpence.next()

    if debt == "В долг":

        await bot.answer_callback_query(call.id)
        await call.message.edit_text(f"Кошелёк: 💼 В долг {creditor}")

        message_id = call.message.message_id + 1

        categories = await bot.transaction.get_categories_of_expences()
        categories_of_expence_kb = expenceKB.create_expence_categories_kb(
            categories, message_id, category_choose)

        await bot.send_message(chat_id, text="Какая категория расхода? 📊", reply_markup=categories_of_expence_kb)

    else:
        await bot.answer_callback_query(call.id)
        await call.message.edit_text(f"Возврат долга: {creditor}")

        await FSMexpence.next()
        await bot.send_message(call.message.chat.id, "Введите сумму: 💲")


async def load_coeff(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['ammount'] = call.data
    await call.message.edit_text(f'Коэффициент 🔢 = {call.data}. Введите сумму: 💲')


type_choose = CallbackData("type_choose", 'action', "type")


async def load_categories(call: types.CallbackQuery, callback_data: dict):
    chat_id = call.message.chat.id
    message_id = callback_data.get("message_id")
    category = callback_data.get("callback_data")

    if category != "Долг":
        types_expence = await bot.transaction.get_types_of_expence(category)
        types_of_expence_kb = expenceKB.create_expence_types_kb(
            types_expence, message_id, move, type_choose)

    else:
        types_expence = await bot.transaction.get_types_of_expence(category)
        types_of_expence_kb = expenceKB.create_expence_types_kb_for_debt(
            types_expence, message_id, move, type_choose)

    await bot.edit_message_reply_markup(chat_id=chat_id, message_id=message_id, reply_markup=types_of_expence_kb)


async def back_to_categories(call: types.CallbackQuery, callback_data: dict):
    chat_id = call.message.chat.id
    message_id = callback_data.get("message_id")

    categories = await bot.transaction.get_categories_of_expences()
    categories_of_expence_kb = expenceKB.create_expence_categories_kb(
        categories, message_id, category_choose)

    await bot.edit_message_reply_markup(chat_id=chat_id, message_id=message_id, reply_markup=categories_of_expence_kb)


async def load_type(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    async with state.proxy() as data:
        type = callback_data.get("type")
        action = callback_data.get("action")

        if action:
            data['type'] = [action, type]
        else:
            data['type'] = type

    await FSMexpence.next()

    await bot.answer_callback_query(call.id)
    await call.message.edit_text(f"Тип расхода: 📊 {type}")

    async with state.proxy() as data:
        if data.get("wallet")[1] == "В долг" and action != "Возврат":
            await bot.send_message(call.message.chat.id, "Введите сумму: 💲\nКоэффициент можно внести так: коэфф * сумма (0,95 * 10000)", reply_markup=expenceKB.сoeff_kb())
        else:
            await bot.send_message(call.message.chat.id, "Введите сумму: 💲")


async def ammount_invalid(message: types.Message):
    return await message.reply("Сумма должна быть числом. 🧮")

edit_or_delete = CallbackData(
    "edit_or_delete", "action", "expence_id", "message_id")


async def load_ammount(message_from: types.Message, state: FSMContext):
    chat_id: str = str(message_from.chat.id)
    async with state.proxy() as data:
        ammount = message_from.text
        ammount_arr = []

        try:
            data['ammount']
            ammount_arr = [data['ammount'], ammount]
        except:
            if ammount.find('*') != -1:
                ammount_arr = ammount.split("*")
            else:
                ammount_arr = ["1", ammount]

        data['ammount'] = ammount_arr
    await FSMexpence.next()
    
    await bot.send_message(chat_id, text="Введите комментарий: 💬")

async def load_comment(message_from: types.Message, state: FSMContext):
    user_id: str = str(message_from.chat.id)

    loan_repayment = False

    async with state.proxy() as data:

        data['comment'] = message_from.text

        if data.get("wallet") == "Проект":  
            data['ammount'] = data.get('ammount')[1]
            await bot.transaction.add_expense(data, FSMexpence.names)

        if data.get("wallet")[1] == "В долг":

            if data.get('type')[0] == "Возврат":
                credit = [data.get('date'), data.get('wallet')[0],
                          data.get('wallet')[1], data.get('ammount')[1], data.get("comment")]

                data["wallet"] = "В долг: " + data.get("wallet")[0]
                data['type'] = "Возврат долга: " + data.get("type")[1]
                data['ammount'] = data['ammount'][1]
                await bot.transaction.add_expense(data, FSMexpence.names)

                await bot.transaction.add_credit(credit)
            else:
                if data.get('ammount')[0] == '1':
                    data["ammount"] = data['ammount'][1]

                    credit = [data.get('date'), data.get('wallet')[0],
                              data.get('wallet')[1], data.get('ammount'), data.get("comment")]

                    data["wallet"] = "В долг: " + data.get("wallet")[0]

                    await bot.transaction.add_expense(data, FSMexpence.names)
                    await bot.transaction.add_credit(credit)
                else:
                    koef = data['ammount'][0]
                    ammount = data['ammount'][1]

                    if ammount.find(",") != -1:
                        ammount = ammount.replace(",", ".")

                    fact_ammount = str(
                        float(koef.replace(",", ".")) * float(ammount)).replace(".", ",")

                    data['ammount'] = fact_ammount

                    credit = [data.get('date'), data.get('wallet')[0],
                              data.get('wallet')[1], data.get('ammount'), data.get("comment")]

                    saving = [koef, ammount, data.get("comment")]

                    data["wallet"] = "В долг: " + \
                        data.get("wallet")[0] + f" Коэф: {koef}"

                    await bot.transaction.add_expense(data, FSMexpence.names)
                    await bot.transaction.add_credit(credit)
                    await bot.transaction.add_saving(saving)

        if data.get("wallet")[1] == "Возврат":

            loan_repayment = True

            credit = [data.get('date'), data.get('wallet')[
                0], data.get('wallet')[1], data['ammount'][1], data.get("comment")]

            await bot.transaction.add_credit(credit)
    await state.finish()

    start_kb = startKB.create_start_kb()

    message_id = message_from.message_id

    if loan_repayment:

        credit_data = await bot.transaction.get_last_credit()
        id = credit_data[0]
        date = credit_data[1]
        creditor = credit_data[2]
        ammount = credit_data[4]
        comment = credit_data[6]

        message = f"Возврат долга: \nДата возврата: 📅 <b>{date}</b>\nКому вернули: 👥 <b>{creditor}</b>\nСколько вернули: 💰 {ammount}\nКомментарий: 💬 {comment}"

        edit_or_delete_kb = generalKB.edit_or_delete_kb(
            id, message_id + 1, edit_or_delete)
        await bot.send_message(user_id, message, parse_mode="HTML", reply_markup=edit_or_delete_kb)

        message = "Выберите следующую операцию: 🔄"
        await bot.send_message(user_id, message, parse_mode="HTML", reply_markup=start_kb)

    else:
        expense_data = await bot.transaction.get_last_expense()
        id = expense_data[0]
        date = expense_data[1]
        wallet = expense_data[2]
        type = expense_data[3]
        ammount = expense_data[4]
        comment = expense_data[6]

        message = f"Расход 💲: \nДата расхода: 📅 <b>{date}</b> \nКошелёк расхода: 💼 <b>{wallet}</b> \nТип расхода: 📊 <b>{type}</b> \nСумма расхода: 💰 {ammount} \nКомментарий: 💬 {comment}"
        edit_or_delete_kb = generalKB.edit_or_delete_kb(
            id, message_id + 1, edit_or_delete)
        await bot.send_message(user_id, message, parse_mode="HTML", reply_markup=edit_or_delete_kb)

        message = "Выберите следующую операцию: 🔄"
        await bot.send_message(user_id, message, parse_mode="HTML", reply_markup=start_kb)

    for i in range(0, message_id - start_message_id + 1):
        try:
            await bot.delete_message(message_from.chat.id, message_id - i)
        except: i += 1

async def delete(call: types.CallbackQuery, callback_data: dict):
    await bot.answer_callback_query(call.id)
    chat_id = call.message.chat.id
    message_id = callback_data.get('message_id')
    expence_id = callback_data.get('expence_id')

    await bot.transaction.delete_expence(expence_id)
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
        start_expence_adding, filters.Regexp(regexp=r"(Расход 💲)"), state=None)
    dp.register_message_handler(
        cancel_handler, filters.Regexp(regexp=r"(Отмена расхода)"), state='*')
    dp.register_message_handler(cancel_handler, state='*', commands='cancle')

    dp.register_callback_query_handler(
        load_date, lambda c: c.data == 'today', state=FSMexpence.date)
    dp.register_message_handler(
        date_invalid,
        lambda message: not (re.match(r'^\d{2}\.\d{2}\.\d{4}$', message.text)),
        state=FSMexpence.date)
    dp.register_message_handler(load_date_text, state=FSMexpence.date)

    dp.register_callback_query_handler(
        load_wallet, wallet_choose.filter(), state=FSMexpence.wallet)
    dp.register_callback_query_handler(
        back_to_wallets, move.filter(move="Назад"), state=FSMexpence.wallet)
    dp.register_callback_query_handler(
        load_creditor, credititors_debt.filter(), state=FSMexpence.wallet)

    dp.register_callback_query_handler(
        load_categories, category_choose.filter(), state=FSMexpence.type)
    dp.register_callback_query_handler(
        back_to_categories, move.filter(move="Назад"), state=FSMexpence.type)
    dp.register_callback_query_handler(
        load_type, type_choose.filter(), state=FSMexpence.type)

    dp.register_message_handler(
        ammount_invalid, lambda message: not (re.match(r'^[\d,* ]+$', message.text)), state=FSMexpence.ammount)

    dp.register_callback_query_handler(
        load_coeff, state=FSMexpence.ammount)

    dp.register_message_handler(load_ammount,  state=FSMexpence.ammount)
    dp.register_message_handler(load_comment,  state=FSMexpence.comment)

    # dp.register_callback_query_handler(edit_expence, cd_edit_byid.filter())
    dp.register_callback_query_handler(
        delete, edit_or_delete.filter(action="Delete"))
    # dp.register_callback_query_handler(
    #     edit, edit_or_delete.filter(action = "Edit"))
    # dp.register_callback_query_handler(
    #     back_to_edit, to_edit.filter(editable_value = "Назад"))
