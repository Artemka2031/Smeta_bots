from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.methods import DeleteMessage
from aiogram.types import Message

from Bot.Keyboards.Operations.category import create_today_kb
from Bot.Routers.AddComing.ComingRouter.amount_router import amountRouter
from Bot.Routers.AddComing.ComingRouter.category_router import categoryRouter
from Bot.Routers.AddComing.ComingRouter.comment_router import commentRouter
from Bot.Routers.AddComing.ComingRouter.date_router import dateRouter
from Bot.Routers.AddComing.coming_state_class import Coming
from Bot.commands import bot_commands

comingsRouter = Router()


@comingsRouter.message(Command(bot_commands.add_coming))
@comingsRouter.message(F.text.casefold() == "приход")
async def start_coming_adding(message: Message, state: FSMContext) -> None:
    await state.clear()
    sent_message = await message.answer(text="Выберете дату прихода:",
                                        reply_markup=create_today_kb())
    await state.update_data(date_message_id=sent_message.message_id)
    await state.set_state(Coming.date)


# @comingsRouter.message(Command("cancel_coming"))
@comingsRouter.message(F.text.casefold() == "отмена прихода")
async def delete_coming_adding(message: Message, state: FSMContext, bot: Bot) -> None:
    chat_id = message.chat.id
    data = await state.get_data()
    await message.delete()

    fields_to_check = ["date_message_id", "category_message_id", "amount_message_id", "comment_message_id"]

    delete_messages = [data[field] for field in fields_to_check if field in data]

    extra_messages = data.get("extra_messages", [])
    delete_messages.extend(extra_messages)

    for message_id in delete_messages:
        await bot(DeleteMessage(chat_id=chat_id, message_id=message_id))

    await message.answer(text="Приход отменён")
    await state.clear()


# Добавляем роутер по работе с датой
comingsRouter.include_router(dateRouter)

# Добавляем роутер для работы с категориями
comingsRouter.include_router(categoryRouter)

# Добавляем роутер для работы с суммой прихода
comingsRouter.include_router(amountRouter)

# Добавляем роутер для работы с комментарием прихода и удалением прихода 
comingsRouter.include_router(commentRouter)
