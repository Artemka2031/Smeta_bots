import asyncio

from aiogram import Dispatcher, Bot
from aiogram.fsm.storage.memory import MemoryStorage

from Bot.commands import get_all_commands
from .Routers.AddExpense import create_expenses_router
from .Routers.Edit.Expense.edit_expense_category_router import create_edit_expense_categories_router
from .Routers.start_router import create_start_router


# async def main():
#     storage = MemoryStorage()
#
#     await bot.set_my_commands(commands=get_all_commands())
#
#     dp = Dispatcher(storage=storage)
#
#     dp.include_router(startRouter)
#
#     dp.include_router(editComingCategoriesRouter)
#     dp.include_router(editExpenseCategoriesRouter)
#
#     dp.include_router(expensesRouter)
#     dp.include_router(comingsRouter)
#
#     await dp.start_polling(bot)


async def setup_routers(dp: Dispatcher, bot: Bot):
    await bot.set_my_commands(commands=get_all_commands())

    start_router = create_start_router(bot)
    dp.include_router(start_router)

    editExpenseCategoriesRouter = create_edit_expense_categories_router()
    expensesRouter = create_expenses_router(bot)

    # dp.include_router(editComingCategoriesRouter)
    dp.include_router(editExpenseCategoriesRouter)
    dp.include_router(expensesRouter)
    # dp.include_router(comingsRouter)


# if __name__ == '__main__':
#     try:
#         print("Бот запущен")
#         asyncio.run(main())
#     except:
#         print('Закрываю бота')
