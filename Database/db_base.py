import logging

from peewee import SqliteDatabase, CharField, Model, IntegrityError, DateField


def initialize_logger(logger_name, log_level=logging.INFO):
    logger = logging.getLogger(logger_name)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)

    logger.addHandler(handler)
    logger.setLevel(log_level)

    return logger


class DatabaseManager:
    current_db = SqliteDatabase(None)

    @staticmethod
    def set_database(path):
        DatabaseManager.current_db.init(path)

    @staticmethod
    def get_database():
        return DatabaseManager.current_db


class BaseModel(Model):
    class Meta:
        abstract = True
        database = DatabaseManager.get_database()


class BaseCategory(BaseModel):
    """
    Represents a generic category used across different types of financial operations.
    Provides methods for creating, retrieving, and managing categories in a database.
    """

    name = CharField(unique=True)
    # Инициализация logger как атрибута класса
    logger = initialize_logger(f"BaseCategory_logger")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = initialize_logger(f"{self.__class__.__name__}_logger")

    @classmethod
    def add(cls, name: str):
        """
        Adds a new category with the specified name to the database.

        :param name: The name of the new category.
        :raises IntegrityError: If a category with the given name already exists.
        """
        try:
            new_category = cls.create(name=name)
            cls.logger.info(f"Category '{new_category.name}' added successfully.")
        except IntegrityError:
            cls.logger.warning(f"Category '{name}' already exists.")
            raise IntegrityError(f"Category '{name}' already exists.")

    @classmethod
    def get_all(cls) -> list:
        """
        Retrieves all categories from the database.

        :return: A list of dicts with 'id' and 'name' for each category.
        """
        try:
            categories = cls.select()
            return [{"id": category.id, "name": category.name} for category in categories]
        except Exception as e:
            cls.logger.error(f"Failed to retrieve categories: {e}")
            return []

    @classmethod
    def get_name_by_id(cls, category_id: int) -> str | None:
        """
        Retrieves a category name by its ID.

        :param category_id: ID of the category to find.
        :return: Name of the category or None if not found.
        """
        try:
            category = cls.get(cls.id == category_id)
            return category.name
        except cls.DoesNotExist:
            cls.logger.warning(f"Category ID {category_id} not found.")
            return None
        except Exception as e:
            cls.logger.error(f"Error: {e}")
            return None

    @classmethod
    def get_id_by_name(cls, name: str) -> int | None:
        """
        Retrieves a category ID by its name.

        :param name: Name of the category to find.
        :return: ID of the category or None if not found.
        """
        try:
            category = cls.get(cls.name == name)
            return category.id
        except cls.DoesNotExist:
            cls.logger.warning(f"Category '{name}' not found.")
            return None
        except Exception as e:
            cls.logger.error(f"Error: {e}")
            return None

    @classmethod
    def change_category_name(cls, category_id, new_category_name):
        """
        Changes the name of an existing category identified by its ID to a new name.

        :param category_id: The ID of the category to be renamed.
        :param new_category_name: The new name for the category.
        :raises DoesNotExist: If no category with the specified ID exists.
        :raises IntegrityError: If a category with the new name already exists.
        """
        try:
            category = cls.get_by_id(category_id)
            category.name = new_category_name
            category.save()  # This might raise IntegrityError if the new name already exists.
            cls.logger.info(f"Category ID {category_id} was successfully renamed to '{new_category_name}'.")
        except cls.DoesNotExist:
            cls.logger.error(f"No category found with ID {category_id}. Unable to rename.")
            raise
        except IntegrityError:
            cls.logger.error(
                f"A category with the name '{new_category_name}' already exists. Cannot rename category ID {category_id}.")
            raise


class BaseType(BaseModel):
    """
    Abstract base class for types associated with categories. This class provides common functionality
    to add, retrieve, and manage types in a database. It should be extended by specific type classes
    that define a `category_class` to associate with a specific category.
    """
    name = CharField(unique=True)
    logger = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Initialize logger using the specialized function
        self.logger = initialize_logger(f"{self.__class__.__name__}_logger")

    @property
    def category_class(self):
        """
        This property should be overridden in child classes to return the associated category class.

        :raises NotImplementedError: If the child class does not implement this property.
        """
        raise NotImplementedError("Child class must define the `category_class` property.")

    @classmethod
    def add_type(cls, type_name, category_id):
        # Теперь правильно используем category_class для доступа к классу категории
        CategoryModel = cls.category_class.fget(None)  # Получаем класс модели категории

        try:
            category = CategoryModel.get(CategoryModel.id == category_id)
            new_type = cls.create(name=type_name, category=category)
            cls.logger.info(f"New type '{new_type.name}' added to category '{category.name}' successfully.")
        except CategoryModel.DoesNotExist:
            cls.logger.error(f"Category with ID {category_id} not found.")
            pass
        except IntegrityError:
            cls.logger.error(f"Type '{type_name}' already exists in category '{category.name}'.")
            raise IntegrityError(f"Type '{type_name}' already exists in category '{category.name}'.")
            pass
        except Exception as e:
            cls.logger.error(f"Error adding type: {e}")
            pass

    @classmethod
    def move_type(cls, type_id: int, from_category_id: int, to_category_id: int):
        """
        Moves a type from one category to another.

        :param type_id: The ID of the type to move.
        :param from_category_id: The ID of the current category of the type.
        :param to_category_id: The ID of the new category for the type.
        """
        try:
            # Ensure both categories exist
            from_category = cls.category_class.get_by_id(from_category_id)
            to_category = cls.category_class.get_by_id(to_category_id)

            # Move the type to the new category
            type_instance = cls.get_by_id(type_id)
            type_instance.category = to_category
            type_instance.save()

            cls.logger.info(f"Type '{type_instance.name}' moved from '{from_category.name}' to '{to_category.name}'.")
        except cls.DoesNotExist as e:
            cls.logger.error(f"Error moving type: {e}")
            raise

    @classmethod
    def get_all_types(cls, category_id: int):
        """
        Retrieves all types within a specific category.

        :param category_id: The ID of the category to retrieve types from.
        :return: A list of type information dictionaries.
        """
        try:
            types = cls.select().where(cls.category_id == category_id)
            return [{"category_id": type_.category_id, "category_name": type_.category.name, "type_id": type_.id,
                     "type_name": type_.name} for type_ in types]
        except Exception as e:
            cls.logger.error(f"Error retrieving types: {e}")
            return []

    @classmethod
    def get_type(cls, category_id: int, type_id):
        CategoryModel = cls.category_class.fget(None)
        try:
            # Поиск исходной категории
            category = CategoryModel.get(CategoryModel.id == category_id)

            # Поиск конкретного типа в данной категории
            expense_type = cls.get((cls.id == type_id) & (cls.category == category))

            return {
                "type_id": expense_type.id,
                "type_name": expense_type.name,
                "category_id": category.id,
                "category_name": category.name
            }
        except cls.DoesNotExist:
            cls.logger.warning(f"Ошибка: Тип с ID {type_id} не найден в данной категории.")
            return None
        except CategoryModel.DoesNotExist:
            cls.logger.warning(f"Ошибка: Категория с ID {category_id} не найдена.")
            return None
        except Exception as e:
            cls.logger.error(f"Ошибка при получении информации о типе: {e}")
            return None

    @classmethod
    def rename_type(cls, type_id: int, new_name: str):
        """
        Renames a specific type by its ID.

        :param type_id: ID of the type to rename.
        :param new_name: New name for the type.
        """
        try:
            type_instance = cls.get_by_id(type_id)
            # Check for uniqueness of the new name within the same category
            if cls.select().where(cls.name == new_name, cls.category_id == type_instance.category_id).exists():
                cls.logger.warning(f"Type name '{new_name}' already exists in the same category.")
                raise IntegrityError(f"Type name '{new_name}' already exists in the same category.")

            old_name = type_instance.name
            type_instance.name = new_name
            type_instance.save()
            cls.logger.info(f"Type name changed from '{old_name}' to '{new_name}'.")
        except cls.DoesNotExist:
            cls.logger.warning(f"Type with ID {type_id} not found.")
        except IntegrityError:
            cls.logger.warning(f"Type name '{new_name}' already exists in the same category.")
            raise IntegrityError(f"Type name '{new_name}' already exists in the same category.")
        except Exception as e:
            cls.logger.error(f"Error renaming type: {e}")


class BaseOperations(BaseModel):
    """
    Abstract base class for financial operations such as expenses and incomes.
    """
    date = DateField()
    amount = CharField()
    comment = CharField()

    logger = initialize_logger("BaseOperationsLogger")

    @classmethod
    def category_class(cls):
        raise NotImplementedError("Subclasses must implement a class method returning the associated category class.")

    @classmethod
    def type_class(cls):
        raise NotImplementedError("Subclasses must implement a class method returning the associated type class.")

    @classmethod
    def add(cls, date, category_id, type_id, amount, comment):
        """
        Adds a new financial operation to the database.
        """
        CategoryModel = cls.category_class()
        TypeModel = cls.type_class()
        try:
            category = CategoryModel.get_by_id(category_id)
            operation_type = TypeModel.get_by_id(type_id)
            operation = cls.create(date=date, category=category, type=operation_type, amount=amount, comment=comment)
            cls.logger.info(
                f"New operation added successfully in type '{operation_type.name}' of category '{category.name}'.")
            return operation
        except IntegrityError as e:
            cls.logger.error(f"Failed to add new operation: {e}")
            raise

    @classmethod
    def remove(cls, operation_id):
        """
        Removes a financial operation from the database by its ID.
        """
        try:
            operation = cls.get_by_id(operation_id)
            operation.delete_instance()
            cls.logger.info(f"Operation with ID {operation_id} was successfully deleted.")
        except cls.DoesNotExist:
            cls.logger.warning(f"Operation with ID {operation_id} not found.")
            raise

    @classmethod
    def get_all(cls):
        """
        Retrieves all financial operations from the database.
        """
        try:
            operations = cls.select()
            return [{
                "id": operation.id,
                "date": operation.date.strftime("%Y-%m-%d"),
                "category_id": operation.category.id if operation.category else None,
                "type_id": operation.type.id if operation.type else None,
                "amount": operation.amount,
                "comment": operation.comment
            } for operation in operations]
        except Exception as e:
            cls.logger.error(f"Failed to retrieve operations: {e}")
            return []

    @classmethod
    def get_by_time_interval(cls, start_date, end_date):
        """
        Retrieves financial operations within a specific time interval.
        """
        try:
            operations = cls.select().where(cls.date.between(start_date, end_date))
            return [{
                "id": operation.id,
                "date": operation.date.strftime("%Y-%m-%d"),
                "category_id": operation.category.id if operation.category else None,
                "type_id": operation.type.id if operation.type else None,
                "amount": operation.amount,
                "comment": operation.comment
            } for operation in operations]
        except Exception as e:
            cls.logger.error(f"Failed to retrieve operations by time interval: {e}")
            return []
