import pygsheets


class GoogleSheets:
    def __init__(self, credentials_file, spreadsheet_url):
        self.client = pygsheets.authorize(service_file=credentials_file)
        self.spreadsheet = self.client.open_by_url(spreadsheet_url)

    def get_worksheet(self, worksheet_name):
        return self.spreadsheet.worksheet_by_title(worksheet_name)
    

    # def get_last_filled_row(self, wks, id_col):
    #     cells_row = wks.rows
    #     for i in range(cells_row, 0, -1):
    #         if (wks.get_value((i, id_col))):
    #             wks.add_rows(1)
    #             return i + 1
    #         else:
    #             if (wks.get_value((i - 1, id_col))):
    #                 return i    

    # def calc_current_id(self, wks, cells_row, id_col) -> int:
    #     if wks.get_value((cells_row - 1, id_col)) != 'id':
    #         previous_id = int(wks.get_value((cells_row - 1, id_col)))
    #     else:
    #         previous_id = 0
    #     return previous_id + 1

    def get_last_filled_row(self, wks, id_col):
        filled_rows = len(wks.get_col(id_col, include_tailing_empty=False))
        all_rows = len(wks.get_col(id_col, include_tailing_empty=True))

        if filled_rows == all_rows:
            wks.add_rows(1)
            return filled_rows + 1
        else: return filled_rows + 1


    def calc_current_id(self, wks, cells_row, id_col) -> int:
        if wks.get_value((cells_row - 1, id_col)) != 'id':
            previous_id = int(wks.get_value((cells_row - 1, id_col)))
        else:
            previous_id = 0
        return previous_id + 1