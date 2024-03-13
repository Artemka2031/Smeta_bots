from Database.Tables.ComingTables import ComingCategory, ComingType, Coming
from Database.Tables.ExpensesTables import ExpenseCategory, ExpenseType, Expense
from Database.db_base import DatabaseManager


def create_tables_with_drop():
    db = DatabaseManager.get_database()
    db.connect()

    tables = [ExpenseCategory, ExpenseType, Expense,
              ComingCategory, ComingType, Coming]
    db.drop_tables(tables, safe=True)
    db.create_tables(tables, safe=True)

    db.close()


if __name__ == '__main__':
    create_tables_with_drop()
