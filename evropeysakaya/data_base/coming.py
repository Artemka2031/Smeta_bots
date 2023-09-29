from evropeysakaya.data_base.google_sheets.google_sheets import GoogleSheets
import requests

from evropeysakaya.data_base.google_sheets.urls import coming_url, delete_url


class Coming(GoogleSheets):
    def __init__(self, credentials_file, spreadsheet_url):
        super().__init__(credentials_file, spreadsheet_url)
        self.worksheet_coming = self.get_worksheet("Приходы")
        self.worksheet_types = self.get_worksheet("Статьи приходов")

    async def get_types_of_comming(self, type_col):
        wks = self.worksheet_types
        types = wks.get_col(type_col, include_tailing_empty=False)
        types.pop(0)
        return types

    async def add_coming(self, data, names, id_col, date_col, type_col, ammount_col, comment_col):
        wks = self.worksheet_coming
        try:
            cells_row = self.get_last_filled_row(wks, id_col)
            id = self.calc_current_id(wks, cells_row, id_col)

            values = [data[i] for i in names]
            values.insert(0, id)

            form_url = coming_url
            urlResponse = form_url+'/formResponse'
            urlReferer = form_url+'/viewform'

            form_data = {
                'entry.821273064': values[id_col - 1],
                'entry.1026532699': values[date_col - 1],
                'entry.1835115776': values[type_col - 1],
                'entry.58596234': values[ammount_col - 1],
                'entry.2062900324': values[comment_col - 2],
            }

            user_agent = {'Referer': urlReferer,
                          'User-Agent': "Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1500.52 Safari/537.36"}

            # update ID column
            wks.update_value((cells_row, id_col), str(id),  parse=None)

            # update date
            wks.update_value((cells_row, date_col), values[date_col - 1])

            # upload type of expence data
            wks.update_value((cells_row, type_col), values[type_col - 1])

            # update done data
            wks.update_value((cells_row, ammount_col), values[ammount_col - 1])

            # update done data
            wks.update_value((cells_row, comment_col), values[comment_col - 2])

            response = requests.post(
                urlResponse, data=form_data, headers=user_agent)
        except:
            return 0

    async def get_last_coming(self, id_col):
        wks = self.worksheet_coming
        row = len(wks.get_col(id_col, include_tailing_empty=False))
        data = wks.get_row(row, include_tailing_empty=False)

        return data

    async def delete_coming(self, to_delete_id, id_col, delete_col):
        wks = self.worksheet_coming

        form_url = delete_url
        urlResponse = form_url+'/formResponse'
        urlReferer = form_url+'/viewform'

        form_data = {
            'entry.365193640': to_delete_id,
            'entry.1870726300': "Приход",
        }

        user_agent = {'Referer': urlReferer,
                      'User-Agent': "Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1500.52 Safari/537.36"}

        row = wks.find(to_delete_id, cols=(id_col, id_col))[0].row
        wks.update_value((row, delete_col), "Удалено")

        response = requests.post(
            urlResponse, data=form_data, headers=user_agent)

        print("Delete coming request is sended", response)
