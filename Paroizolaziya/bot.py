import asyncio
from aiogram.utils import executor
from Paroizolaziya.create_bot import dp

from Paroizolaziya.handlers import coming, start, expenses

start.register_handlers_admin(dp)
expenses.register_handlers_admin(dp)
coming.register_handlers_admin(dp)

# if __name__ == "__main__":
#     executor.start_polling(dp, skip_updates=True)

def start_par_bot():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    executor.start_polling(dp, skip_updates=True, loop=loop)
