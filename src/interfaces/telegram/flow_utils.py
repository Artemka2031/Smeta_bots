from __future__ import annotations

from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from src.interfaces.telegram.keyboards.start_kb import create_start_kb

from .state_utils import delete_message_ids


async def send_next_operation_prompt(bot, chat_id: int) -> None:
    await bot.send_message(
        chat_id=chat_id,
        text="Выберите следующую операцию:",
        reply_markup=create_start_kb(),
    )


async def cancel_operation_flow(
    bot,
    message: Message,
    state: FSMContext,
    *,
    tracked_fields: list[str],
    cancel_text: str,
) -> None:
    data = await state.get_data()
    await message.delete()

    message_ids = [data[field] for field in tracked_fields if field in data]
    message_ids.extend(data.get("extra_messages") or [])

    await delete_message_ids(bot, message.chat.id, message_ids, bot.logger)
    await message.answer(text=cancel_text)
    await state.clear()
