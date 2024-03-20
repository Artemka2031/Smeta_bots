from aiogram import Dispatcher, Bot

from Bot.commands import get_all_commands
from .Routers import create_expenses_router, create_start_router


async def setup_routers(dp: Dispatcher, bot: Bot):
    await bot.set_my_commands(commands=get_all_commands())

    start_router = create_start_router()
    dp.include_router(start_router)

    expensesRouter = create_expenses_router(bot)
    dp.include_router(expensesRouter)

    # dp.include_router(comingsRouter)

