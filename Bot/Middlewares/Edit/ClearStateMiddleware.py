from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.dispatcher.flags import get_flag
from aiogram.exceptions import TelegramBadRequest
from aiogram.methods import DeleteMessage
from aiogram.types import CallbackQuery

class ClearStateMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[CallbackQuery, Dict[str, Any]], Awaitable[Any]],
            event: CallbackQuery,
            data: Dict[str, Any]
    ) -> Any:
        delete_sent_text_flag = get_flag(data, "delete_sent_message")
        if delete_sent_text_flag is None:
            return await handler(event, data)

        chat_id = event.message.chat.id
        state = data["state"]
        try:
            sent_message = (await state.get_data())["sent_message"]
            await state.clear()
            await bot(DeleteMessage(chat_id=chat_id, message_id=sent_message))
        except KeyError:
            await state.clear()
        except TelegramBadRequest:
            pass

        return await handler(event, data)
