from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from Database.Tables.ComingTables import ComingCategory, ComingType
from Bot.Keyboards.Edit.category import create_category_choose_kb
from Bot.Keyboards.Edit.type import BackToCategoriesEditCallback, BackToTypesCallback, ChooseTypeEditCallback, \
    create_edit_type_kb, create_type_choose_kb
from .Type_routers import deleteTypeRouter, renameTypeRouter, newTypeRouter

typeEditRouter = Router()


# Работа с типами
@typeEditRouter.callback_query(ChooseTypeEditCallback.filter(F.operation == "coming"),
                               flags={"delete_sent_message": True})
async def edit_type_callback(query: CallbackQuery, callback_data: ChooseTypeEditCallback, state: FSMContext):
    await query.answer()

    category_id = callback_data.category_id
    type_id = callback_data.type_id

    category_name = callback_data.category_name
    type_name = callback_data.type_name

    await query.message.edit_text(text=f'Выберите действие по изменению типа \n'
                                       f'"{type_name}" в категории "{category_name}":',
                                  reply_markup=create_edit_type_kb(category_id, type_id, ComingType))


@typeEditRouter.callback_query(BackToTypesCallback.filter((F.back == True) and F.operation == "coming"),
                               flags={"delete_sent_message": True})
async def back_to_types_callback(query: CallbackQuery, callback_data: BackToTypesCallback):
    await query.answer()

    category_id = callback_data.category_id
    category_name = ComingCategory.get_name_by_id(category_id)

    await query.message.edit_text(text=f'Выберите тип для изменения \nв категории: "{category_name}"',
                                  reply_markup=create_type_choose_kb(category_id=category_id, OperationType=ComingType,
                                                                     OperationCategory=ComingCategory, create=True))


# Добавляем роутер по изменению имени типа
typeEditRouter.include_router(renameTypeRouter)

# Добавляем роутер по удалению типа
typeEditRouter.include_router(deleteTypeRouter)

# Добавляем роутер по добавлению нового типа
typeEditRouter.include_router(newTypeRouter)


@typeEditRouter.callback_query(BackToCategoriesEditCallback.filter((F.back == True) and (F.operation == "coming")),
                               flags={"delete_sent_message": True})
async def back_to_categories_callback(query: CallbackQuery):
    await query.answer()

    await query.message.edit_text(text=f"Выберите категория для изменения",
                                  reply_markup=create_category_choose_kb(OperationCategory=ComingCategory,
                                                                         category_create=True))
