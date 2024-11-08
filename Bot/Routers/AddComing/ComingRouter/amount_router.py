from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from Bot.Filters.check_amount import CheckAmount
from Bot.Routers.AddComing.coming_state_class import Coming
from Bot.create_bot import ProjectBot


def create_amount_router(bot: ProjectBot):
    amount_router = Router()

    @amount_router.message(Coming.amount, CheckAmount(F.text))
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

        await state.set_state(Coming.amount)

    @amount_router.message(Coming.amount)
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

        comment_message = await bot.send_message(chat_id=message.chat.id, text="Введите комментарий:")
        await state.update_data(comment_message_id=comment_message.message_id)
        await state.set_state(Coming.comment)

    return amount_router
