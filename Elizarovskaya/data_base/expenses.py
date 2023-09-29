
from Elizarovskaya.data_base.google_sheets.google_sheets import GoogleSheets
import requests


class Expenses(GoogleSheets):
    def __init__(self, credentials_file, spreadsheet_url):
        super().__init__(credentials_file, spreadsheet_url)
        self.worksheet_expenses = self.get_worksheet("Расходы")
        self.worksheet_categories = self.get_worksheet("Статьи расходов")

    async def get_categories_of_expences(self, categories_row):
        try:
            wks = self.worksheet_categories
            categories_of_expences = wks.get_values(
                (categories_row, 1), (categories_row, wks.cols))[0]

            return categories_of_expences
        except:
            return 0

    async def get_types_of_expence(self, category):
        wks = self.worksheet_categories

        for i, category_name in enumerate(wks.get_row(1)):
            if category_name.lower() == category.lower():
                # Если категория совпадает, получаем все типы расходов для этой категории
                types = wks.get_col(i+1, include_tailing_empty=False)
                types.pop(0)
                return types

        # Если категория не найдена, возвращаем пустой список
        return []

    async def add_expense(self, data, names, id_col, wallet_col, date_col, type_col, ammount_col, comment_col):
        wks = self.worksheet_expenses

        try:
            cells_row = self.get_last_filled_row(wks, id_col)
            id = self.calc_current_id(wks, cells_row, id_col)

            values = [data[i] for i in names]

            values.insert(0, id)

            print(values)

            form_url = "https://docs.google.com/forms/d/e/1FAIpQLSfO_xEbA_vKktkq_lsNRHmwJOyZIgDhGJfV-Z_VrSU8330oQA"
            urlResponse = form_url+'/formResponse'
            urlReferer = form_url+'/viewform'

            form_data = {
                'entry.1083509212': values[id_col - 1],
                'entry.1578939430': values[wallet_col - 1],
                'entry.353006017': values[date_col - 1],
                'entry.222430906': values[type_col - 1],
                'entry.1653797818': values[ammount_col - 1],
                'entry.534980233': values[comment_col - 2]
            }

            user_agent = {'Referer': urlReferer,
                          'User-Agent': "Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1500.52 Safari/537.36"}

            # update ID column
            wks.update_value((cells_row, id_col), str(id),  parse=None)

            # update wallet
            wks.update_value((cells_row, wallet_col), values[wallet_col - 1])

            # update date
            wks.update_value((cells_row, date_col), values[date_col - 1])

            # upload type of expence data
            wks.update_value((cells_row, type_col), values[type_col - 1])

            # update done data
            wks.update_value((cells_row, ammount_col), values[ammount_col - 1])

            # update comment data
            wks.update_value((cells_row, comment_col), values[comment_col - 2])

            response = requests.post(
                urlResponse, data=form_data, headers=user_agent)

            print("Add expense request is sended", response)
        except:
            return 0

    async def get_last_expense(self, id_col):
        wks = self.worksheet_expenses
        row = len(wks.get_col(id_col, include_tailing_empty=False))
        data = wks.get_row(row, include_tailing_empty=False)

        return data

    async def delete_expence(self, to_delete_id, id_col, delete_col):
        wks = self.worksheet_expenses

        form_url = "https://docs.google.com/forms/d/e/1FAIpQLSdIuRgIbdVjE3uxkgQoVb42lCvcxHqV6eO-Ty7PrgzTX94dOg"
        urlResponse = form_url+'/formResponse'
        urlReferer = form_url+'/viewform'

        form_data = {
            'entry.365193640': to_delete_id,
            'entry.1870726300': "Расход",
        }

        user_agent = {'Referer': urlReferer,
                      'User-Agent': "Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1500.52 Safari/537.36"}

        row = wks.find(to_delete_id, cols=(id_col, id_col))[0].row
        wks.update_value((row, delete_col), "Удалено")

        response = requests.post(
            urlResponse, data=form_data, headers=user_agent)

        print("Delete expense request is sended", response)

    # async def edit_expence(seld, data)
