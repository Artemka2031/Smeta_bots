from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from src.interfaces.telegram.filters.check_amount import CheckAmount
from src.interfaces.telegram.routers.add_coming.coming_state_class import Coming
from src.interfaces.telegram.project_bot import ProjectBot
from src.interfaces.telegram.state_utils import clear_extra_messages, ensure_extra_message


def create_amount_router(bot: ProjectBot):
    amount_router = Router()

    @amount_router.message(Coming.amount, CheckAmount(F.text))
    async def incorrect_amount(message: Message, state: FSMContext):
        await message.delete()
        await ensure_extra_message(
            bot,
            state,
            message.chat.id,
            'Введено недопустимое значение. Должны быть только числа больше 0. Разделяющий знак = ","',
        )

        await state.set_state(Coming.amount)

    @amount_router.message(Coming.amount)
    async def set_amount(message: Message, state: FSMContext):
        chat_id = message.chat.id
        await clear_extra_messages(bot, state, chat_id, bot.logger)

        amount_message_id = (await state.get_data())["amount_message_id"]
        amount = float(message.text.replace(',', '.'))

        await state.update_data(amount=amount)
        await bot.edit_message_text(chat_id=chat_id, message_id=amount_message_id, text=f"Введённая сумма: {amount}")
        await message.delete()

        comment_message = await bot.send_message(chat_id=message.chat.id, text="Введите комментарий:")
        await state.update_data(comment_message_id=comment_message.message_id)
        await state.set_state(Coming.comment)

    return amount_router
