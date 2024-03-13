from peewee import ForeignKeyField

from Database.db_base import BaseCategory, BaseType, BaseOperations, initialize_logger


class ExpenseCategory(BaseCategory):
    """
    Represents a category of expenses.
    """

    logger = initialize_logger(f"ExpenseCategory")

    @classmethod
    def delete_category(cls, category_id):
        """
        Deletes an expense category and all associated expense types.

        :param category_id: The ID of the category to be deleted.
        :raises DoesNotExist: If no category with the specified ID exists.
        """
        try:
            # Находим и удаляем все типы расходов, связанные с этой категорией
            types_in_category = ExpenseType.select().where(ExpenseType.category == category_id)
            for expense_type in types_in_category:
                ExpenseType.delete_type(expense_type.id)

            # Удаляем саму категорию
            category = cls.get_by_id(category_id)
            category.delete_instance()
            cls.logger.info(f"Category ID {category_id} and all associated types were successfully deleted.")
        except cls.DoesNotExist:
            cls.logger.error(f"No category found with ID {category_id}. Unable to delete.")
            raise

    class Meta:
        db_table = 'expense_categories'


class ExpenseType(BaseType):
    """
    Represents a type of expense within a category.
    """
    category = ForeignKeyField(ExpenseCategory, backref='expense_types')
    logger = initialize_logger(f"ExpenseType")

    @classmethod
    def delete_type(cls, type_id):
        """
        Deletes an expense type and all associated expenses.

        :param type_id: int, The ID of the expense type to be deleted.
        """
        # Находим все расходы, связанные с этим типом, и удаляем их
        expenses = Expense.select().where(Expense.type == type_id)
        print(expenses)
        for expense in expenses:
            expense.delete_instance()

        # Удаляем сам тип расхода
        type_instance = cls.get_by_id(type_id)
        type_instance.delete_instance()
        cls.logger.info(f"ExpenseType with ID {type_id} and all associated expenses were successfully deleted.")

    @property
    def category_class(self):
        return ExpenseCategory

    class Meta:
        db_table = 'expense_types'


class Expense(BaseOperations):
    """
    Represents an expense operation, including its date, category, type, amount, and an optional comment.
    """
    category = ForeignKeyField(ExpenseCategory, backref='expenses')
    type = ForeignKeyField(ExpenseType, backref='expenses')
    logger = initialize_logger(f"Expense")

    class Meta:
        db_table = 'expenses'

    @classmethod
    def category_class(cls):
        """
        Returns the ExpenseCategory class associated with ExpenseOperation.
        """
        return ExpenseCategory

    @classmethod
    def type_class(cls):
        """
        Returns the ExpenseType class associated with ExpenseOperation.
        """
        return ExpenseType
