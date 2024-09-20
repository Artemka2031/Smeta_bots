# Bot/Utils/router_helpers.py

from typing import List

from aiogram.fsm.context import FSMContext

from Bot.create_bot import ProjectBot


async def delete_messages(bot: ProjectBot, chat_id: int, message_ids: List[int]):
    """
    Удаляет список сообщений в чате.
    """
    for message_id in message_ids:
        try:
            await bot.delete_message(chat_id=chat_id, message_id=message_id)
        except Exception as e:
            bot.logger.error(f"Не удалось удалить сообщение {message_id}: {e}")


async def update_state_data(state: FSMContext, data: dict):
    """
    Обновляет данные состояния.
    """
    await state.update_data(**data)


async def clear_extra_messages(bot: ProjectBot, state: FSMContext, chat_id: int):
    """
    Удаляет все дополнительные сообщения из состояния.
    """
    data = await state.get_data()
    extra_messages = data.get("extra_messages", [])
    if extra_messages:
        await delete_messages(bot, chat_id, extra_messages)
        await state.update_data(extra_messages=[])
