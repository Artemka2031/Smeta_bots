from peewee import ForeignKeyField

from Database.db_base import BaseCategory, BaseType, BaseOperations, initialize_logger


class ComingCategory(BaseCategory):
    """
    Represents a category of income.
    """
    logger = initialize_logger(f"ComingCategory")

    @classmethod
    def delete_category(cls, category_id):
        """
        Deletes a coming category and all associated coming types.

        :param category_id: The ID of the category to be deleted.
        :raises DoesNotExist: If no category with the specified ID exists.
        """
        try:
            # Находим и удаляем все типы приходов, связанные с этой категорией
            types_in_category = ComingType.select().where(ComingType.category == category_id)
            for coming_type in types_in_category:
                ComingType.delete_type(coming_type.id)

            # Удаляем саму категорию
            category = cls.get_by_id(category_id)
            category.delete_instance()
            cls.logger.info(f"Coming category ID {category_id} and all associated types were successfully deleted.")
        except cls.DoesNotExist:
            cls.logger.error(f"No coming category found with ID {category_id}. Unable to delete.")
            raise

    class Meta:
        db_table = 'coming_categories'


class ComingType(BaseType):
    """
    Represents a type of income within a category.
    """
    category = ForeignKeyField(ComingCategory, backref='coming_types')
    logger = initialize_logger(f"ComingType")

    @property
    def category_class(self):
        return ComingCategory

    @classmethod
    def delete_type(cls, type_id):
        """
        Deletes an income type and all associated incomes.

        :param type_id: int, The ID of the income type to be deleted.
        """
        # Находим все доходы, связанные с этим типом, и удаляем их
        comings = Coming.select().where(Coming.type == type_id)
        for coming in comings:
            coming.delete_instance()

        # Удаляем сам тип дохода
        type_instance = cls.get_by_id(type_id)
        type_instance.delete_instance()
        cls.logger.info(f"ComingType with ID {type_id} and all associated incomes were successfully deleted.")

    class Meta:
        db_table = 'coming_types'


class Coming(BaseOperations):
    """
    Represents an income operation, including its date, category, type, amount, and an optional comment.
    """
    category = ForeignKeyField(ComingCategory, backref='comings')
    type = ForeignKeyField(ComingType, backref='comings')
    logger = initialize_logger(f"Coming")

    class Meta:
        db_table = 'comings'

    @classmethod
    def category_class(cls):
        """
        Returns the ComingCategory class associated with ComingOperation.
        """
        return ComingCategory

    @classmethod
    def type_class(cls):
        """
        Returns the ComingType class associated with ComingOperation.
        """
        return ComingType

