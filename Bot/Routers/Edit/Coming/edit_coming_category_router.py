from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from Database.Tables.ComingTables import ComingCategory
from Bot.Keyboards.Edit.category import create_category_choose_kb
from Bot.Middlewares.Edit.ClearStateMiddleware import ClearStateMiddleware
from Bot.commands import bot_commands
from .CategoryRouter import categoryEditRouter
from .TypeRouter import typeEditRouter

editComingCategoriesRouter = Router()


# Методы для запуска работы с редактором категорий и типов
@editComingCategoriesRouter.message(Command(bot_commands.edit_comings))
@editComingCategoriesRouter.message(F.text.casefold() == "редактирование категорий")
async def start_messaging(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(text="Выберите категорию для изменения",
                         reply_markup=create_category_choose_kb(OperationCategory=ComingCategory,
                                                                category_create=True))


editComingCategoriesRouter.callback_query.middleware(ClearStateMiddleware())

editComingCategoriesRouter.include_router(categoryEditRouter)
editComingCategoriesRouter.include_router(typeEditRouter)
