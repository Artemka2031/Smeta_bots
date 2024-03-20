from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.utils.markdown import hbold

from Bot.Keyboards.start_kb import create_start_kb


def create_start_router():
    router = Router()

    @router.message(CommandStart())
    async def start_messaging(message: Message) -> None:
        await message.answer(text=f"Здравствуйте! Приступим к записи расходов и приходов",
                             reply_markup=create_start_kb())

    return router
