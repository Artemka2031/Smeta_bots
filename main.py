from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.types import Message
import asyncio

token = "6587921784:AAE-mMJSPH68hVCh_xrWD4aDk6G3ZZhZlEY"


async def get_started(message: Message, bot: Bot):
    await message.answer(text="Привет!")


async def start():
    bot = Bot(token=token, parse_mode=ParseMode.HTML)
    dp = Dispatcher

    dp.include_router()

    try:
        await dp.start_polling(bots=bot)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(start())