from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from Bot.Filters.check_amount import CheckAmount
from Bot.Routers.AddExpense.expense_state_class import Expense
from Bot.create_bot import ProjectBot
from GoogleSheets.google_sheets import logger


def create_amount_router(bot: ProjectBot):
    amount_router = Router()

    @amount_router.message(Expense.amount, CheckAmount(F.text))
    async def incorrect_amount(message: Message, state: FSMContext):
        await message.delete()

        try:
            extra_messages = (await state.get_data())["extra_messages"]
            if extra_messages is None:
                raise
        except:
            incorrect_amount_message = await bot.send_message(
                chat_id=message.chat.id,
                text='Введено недопустимое значение. Должны быть только числа больше 0. Разделяющий знак = ","')
            incorrect_amount_message_id = incorrect_amount_message.message_id
            await state.update_data(extra_messages=[incorrect_amount_message_id])

        await state.set_state(Expense.amount)

    @amount_router.message(Expense.amount)
    async def set_amount(message: Message, state: FSMContext):
        chat_id = message.chat.id

        try:
            extra_messages = (await state.get_data())["extra_messages"]

            for message_id in extra_messages:
                try:
                    await bot.delete_message(chat_id=chat_id, message_id=message_id)
                except:
                    pass
        except KeyError:
            pass

        amount_message_id = (await state.get_data())["amount_message_id"]
        amount = float(message.text.replace(',', '.'))

        await state.update_data(amount=amount)
        await bot.edit_message_text(chat_id=chat_id, message_id=amount_message_id, text=f"Введённая сумма: {amount}")
        await message.delete()

        data = await state.get_data()
        wallet = data["wallet"]

        if wallet == "Взять в долг":
            saving_message = await bot.send_message(chat_id=chat_id, text="Введите коэффициент экономии:")

            try:
                extra_messages = data["extra_messages"]
                await state.update_data(extra_messages=extra_messages + [saving_message.message_id])
            except KeyError:
                await state.update_data(extra_messages=[saving_message.message_id])

            await state.set_state(Expense.coefficient)
        else:
            comment_message = await bot.send_message(chat_id=message.chat.id, text="Введите комментарий:")
            await state.update_data(comment_message_id=comment_message.message_id)
            await state.set_state(Expense.comment)

    @amount_router.message(Expense.coefficient)
    async def set_coefficient(message: Message, state: FSMContext):

        data = await state.get_data()
        amount_message_id = data["amount_message_id"]
        amount = data["amount"]
        extra_messages = data["extra_messages"]

        try:
            coefficient = float(message.text.replace(',', '.'))
        except ValueError:
            await message.delete()
            logger.info("Введено недопустимое значение. Должны быть только числа больше 0. Разделяющий знак = ','")
            extera_message = await bot.send_message(message.chat.id,
                                                    "Введено недопустимое значение. Должны быть только числа больше 0. Разделяющий знак = ',' ")
            extra_messages.append(extera_message.message_id)
            await state.update_data(extra_messages=extra_messages)

            await state.set_state(Expense.coefficient)
            return

        try:
            for message_id in extra_messages:
                try:
                    await bot.delete_message(chat_id=message.chat.id, message_id=message_id)
                except:
                    pass
        except KeyError:
            pass

        await bot.edit_message_text(chat_id=message.chat.id, message_id=amount_message_id,
                                    text=f"Введённая сумма: {amount}\n"
                                         f"Введённый коэффициент: {coefficient}")

        await state.update_data(coefficient=coefficient)
        await message.delete()

        chat_id = message.chat.id
        comment_message = await bot.send_message(chat_id=chat_id, text="Введите комментарий")
        await state.update_data(comment_message_id=comment_message.message_id)
        await state.set_state(Expense.comment)

    return amount_router
