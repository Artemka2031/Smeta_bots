import requests
from Apollo.data_base.google_sheets.google_sheets import GoogleSheets
from Apollo.data_base.expenses import Expenses


class General(GoogleSheets):
    def __init__(self, credentials_file, spreadsheet_url):
        super().__init__(credentials_file, spreadsheet_url)
        self.expenses = Expenses(credentials_file, spreadsheet_url)
        self.worksheet_wallets = self.get_worksheet("Кошельки")
        self.worksheet_creditors = self.get_worksheet("Долговой кошелёк")
        self.worksheet_credit = self.get_worksheet("Кредиты")
        self.worksheet_saving = self.get_worksheet("Экономия")

    async def get_wallets(self, wallet_col):
        wks = self.worksheet_wallets
        wallets = wks.get_col(wallet_col, include_tailing_empty=False)
        wallets.pop(0)
        return wallets

    async def get_creditors(self, creditors_col):
        wks = self.worksheet_creditors
        creditors = wks.get_col(creditors_col, include_tailing_empty=False)
        creditors.pop(0)
        return creditors

    async def add_credit(self, data, id_col, date_col, creditor_col, type_col, ammount_col, comment_col):
        wks = self.worksheet_credit

        try:
            cells_row = self.get_last_filled_row(wks, id_col)
            id = (await self.expenses.get_last_expense(1))[0]

            data.insert(0, id)

            form_url = "https://docs.google.com/forms/d/e/1FAIpQLSd-pu17GAKjjzM4q3WB3ru8jTpPG2suLqwsSH97u0aEJvlqHw"
            urlResponse = form_url+'/formResponse'
            urlReferer = form_url+'/viewform'

            form_data = {
                'entry.1786488065': data[id_col - 1],
                'entry.378827042': data[date_col - 1],
                'entry.1217436589': data[creditor_col - 1],
                'entry.373997044': data[type_col - 1],
                'entry.1568408638': data[ammount_col - 1],
                'entry.198500734': data[comment_col - 2]
            }

            user_agent = {'Referer': urlReferer,
                          'User-Agent': "Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1500.52 Safari/537.36"}

            # update ID column
            wks.update_value((cells_row, id_col), str(id),  parse=None)

            # update date
            wks.update_value((cells_row, date_col), data[date_col - 1])

            # upload creditor of expence data
            wks.update_value((cells_row, creditor_col), data[creditor_col - 1])

            # update done data
            wks.update_value((cells_row, type_col), data[type_col - 1])

            # update ammount data
            wks.update_value((cells_row, ammount_col), data[ammount_col - 1])

            # update comment data
            wks.update_value((cells_row, comment_col), data[comment_col - 2])

            response = requests.post(
                urlResponse, data=form_data, headers=user_agent)

            print("credit requets is sended", response)
        except:
            return 0
        
    async def add_saving(self, data, id_col, coeff_col, ammount_col, comment_col):
        wks = self.worksheet_saving

        try:
            cells_row = self.get_last_filled_row(wks, id_col)
            id = (await self.expenses.get_last_expense(1))[0]
            data.insert(0, id)

            form_url = "https://docs.google.com/forms/d/e/1FAIpQLScv6wiGOANEJIJIhdIJZKS8nYcbN0s2E1frFVDC7dB0B1KqNg"
            urlResponse = form_url+'/formResponse'
            urlReferer = form_url+'/viewform'

            form_data = {
                'entry.910351070': data[id_col - 1],
                'entry.1082380198': data[coeff_col - 1],
                'entry.1912426092': data[ammount_col - 1],
                'entry.632844609': data[comment_col - 2],
            }

            user_agent = {'Referer': urlReferer,
                          'User-Agent': "Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1500.52 Safari/537.36"}
            
            # update ID column
            wks.update_value((cells_row, id_col), str(id),  parse=None)

            # update coeff
            wks.update_value((cells_row, coeff_col), data[coeff_col - 1])

            # upload ammount
            wks.update_value((cells_row, ammount_col), data[ammount_col - 1])

            # upload comment
            wks.update_value((cells_row, comment_col), data[comment_col - 2])

            response = requests.post(
                urlResponse, data=form_data, headers=user_agent)
            
            print("saving requets is sended", response)
        except: return -1

    async def get_last_cedit(self, id_col):
        wks = self.worksheet_credit
        row = len(wks.get_col(id_col, include_tailing_empty=False))
        data = wks.get_row(row, include_tailing_empty=False)

        return data
