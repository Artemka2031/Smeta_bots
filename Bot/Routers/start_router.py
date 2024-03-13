from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.utils.markdown import hbold

startRouter = Router()


@startRouter.message(CommandStart())
async def start_messaging(message: Message) -> None:
    await message.answer(f"Привет,{hbold(message.from_user.full_name)}, я твой личный финансовый помощник!")


def create_start_router(bot):
    router = Router()

    @router.message(CommandStart())
    async def start_messaging(message: Message) -> None:
        await message.answer(f"Привет, {hbold(message.from_user.full_name)}, я твой личный финансовый помощник!")

    return router