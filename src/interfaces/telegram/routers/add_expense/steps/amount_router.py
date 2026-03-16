from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from src.interfaces.telegram.filters.check_amount import CheckAmount
from src.interfaces.telegram.routers.add_expense.expense_state_class import Expense
from src.interfaces.telegram.project_bot import ProjectBot
from src.interfaces.telegram.state_utils import clear_extra_messages, ensure_extra_message


def create_amount_router(bot: ProjectBot):
    amount_router = Router()

    @amount_router.message(Expense.amount, CheckAmount(F.text))
    async def incorrect_amount(message: Message, state: FSMContext):
        await message.delete()
        await ensure_extra_message(
            bot,
            state,
            message.chat.id,
            'Введено недопустимое значение. Должны быть только числа больше 0. Разделяющий знак = ","',
        )

        await state.set_state(Expense.amount)

    @amount_router.message(Expense.amount)
    async def set_amount(message: Message, state: FSMContext):
        chat_id = message.chat.id

        data = await state.get_data()
        await clear_extra_messages(bot, state, chat_id, bot.logger)

        # Получаем сообщение с суммой
        amount_message_id = data.get("amount_message_id")
        amount = float(message.text.replace(',', '.'))

        # Обновляем сумму в состоянии
        await state.update_data(amount=amount)
        await bot.edit_message_text(chat_id=chat_id, message_id=amount_message_id, text=f"Введённая сумма: {amount}")
        await message.delete()

        # Переходим к следующему шагу, в зависимости от кошелька
        wallet = data["wallet"]
        if wallet == "Взять в долг":
            saving_message = await bot.send_message(chat_id=chat_id, text="Введите коэффициент экономии:")

            extra_messages = data.get("extra_messages") or []
            extra_messages.append(saving_message.message_id)
            await state.update_data(extra_messages=extra_messages)

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
        try:
            coefficient = float(message.text.replace(',', '.'))
        except ValueError:
            await message.delete()
            await ensure_extra_message(
                bot,
                state,
                message.chat.id,
                "Введено недопустимое значение. Должны быть только числа больше 0. Разделяющий знак = ',' ",
            )
            await state.set_state(Expense.coefficient)
            return

        # Удаляем дополнительные сообщения, если они есть
        await clear_extra_messages(bot, state, message.chat.id, bot.logger)

        # Обновляем сообщение с суммой и коэффициентом
        await bot.edit_message_text(chat_id=message.chat.id, message_id=amount_message_id,
                                    text=f"Введённая сумма: {amount}\n"
                                         f"Введённый коэффициент: {coefficient}")

        await state.update_data(coefficient=coefficient)
        await message.delete()

        # Переходим к следующему шагу (ввод комментария)
        comment_message = await bot.send_message(chat_id=message.chat.id, text="Введите комментарий:")
        await state.update_data(comment_message_id=comment_message.message_id)
        await state.set_state(Expense.comment)

    return amount_router
