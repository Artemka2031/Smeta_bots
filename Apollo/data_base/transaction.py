from Apollo.data_base.expenses import Expenses
from Apollo.data_base.general import General
from Apollo.data_base.coming import Coming


class Transaction(Expenses):
    def __init__(self, credentials_file, spreadsheet_url):
        super().__init__(credentials_file, spreadsheet_url)
        self.expenses = Expenses(credentials_file, spreadsheet_url)
        self.general = General(credentials_file, spreadsheet_url)
        self.coming = Coming(credentials_file, spreadsheet_url)

    # Coming
    async def get_types_of_comming(self, type_col: int = 1):\
        return await self.coming.get_types_of_comming(type_col)
    
    async def add_coming(self, data, names, id_col: int = 1,
                        date_col: int = 2, type_col: int = 3,
                        ammount_col: int = 4, comment_col: int = 6):
        return await self.coming.add_coming(data, names, id_col, date_col, type_col, ammount_col, comment_col)
    
    async def get_last_coming(self, id_col: int = 1):
        return await self.coming.get_last_coming(id_col)
    
    async def delete_coming(self, to_delete_id,
                             id_col: int = 1,
                             delete_col: int = 5,
                             ):
        await self.coming.delete_coming(to_delete_id, id_col, delete_col)

    # Expenses
    async def get_categories_of_expences(self, categories_row: int = 1):
        return await self.expenses.get_categories_of_expences(categories_row)

    async def get_types_of_expence(self, category: str):
        return await self.expenses.get_types_of_expence(category)

    async def add_expense(self, data, names,
                          id_col: int = 1,
                          wallet_col: int = 2,
                          date_col: int = 3,
                          type_col: int = 4,
                          ammount_col: int = 5,
                          comment_col: int = 7 
                          ):
        return await self.expenses.add_expense(data, names, id_col, wallet_col,
                                               date_col, type_col, ammount_col, comment_col)

    async def get_last_expense(self, id_col: int = 1):
        return await self.expenses.get_last_expense(id_col)

    async def delete_expence(self, to_delete_id,
                             id_col: int = 1,
                             delete_col: int = 6,
                             ):
        await self.expenses.delete_expence(to_delete_id, id_col, delete_col)

    # General
    async def get_wallets(self, wallet_col: int = 1):
        return await self.general.get_wallets(wallet_col)

    async def get_creditors(self, creditors_col: int = 1):
        return await self.general.get_creditors(creditors_col)

    async def add_credit(self, data, id_col: int = 1, date_col: int = 2,
                         creditor_col: int = 3, type_col: int = 4,
                         ammount_col: int = 5, comment_col: int = 7):
        return await self.general.add_credit(data, id_col, date_col, creditor_col, type_col, ammount_col, comment_col)
    
    async def get_last_credit(self, id_col: int = 1):
        return await self.general.get_last_cedit(id_col)
    
    async def add_saving(self, data, id_col: int = 1, coeff_col: int = 2, 
                        ammount_col: int = 3, comment_col: int = 5):
        return await self.general.add_saving(data, id_col, coeff_col, ammount_col, comment_col)
