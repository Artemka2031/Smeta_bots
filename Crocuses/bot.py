import asyncio
from aiogram.utils import executor
from Crocuses.create_bot import dp

from Crocuses.handlers import coming, start, expenses

start.register_handlers_admin(dp)
expenses.register_handlers_admin(dp)
coming.register_handlers_admin(dp)


def start_croc_bot():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    executor.start_polling(dp, skip_updates=True, loop=loop)
