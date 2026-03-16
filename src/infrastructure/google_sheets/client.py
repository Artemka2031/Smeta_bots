from __future__ import annotations

import re

import pygsheets

from src.management.logging import get_logger
from .cell_writer import WorksheetCellWriter
from .creditor_locator import CreditorBlockLocator


class GoogleSheetsClient:
    def __init__(self, spreadsheet_url: str, service_account_json: str, project_key: str | None = None) -> None:
        if not service_account_json:
            raise ValueError("Google service account credentials are required")

        self.service_account_json = service_account_json
        self.client = pygsheets.authorize(service_account_json=self.service_account_json)
        self.sh = self.client.open_by_url(spreadsheet_url)
        self.ws = self.sh.worksheet_by_title("Общая таблица")
        self._logger = get_logger("google-sheets", color="yellow", project_key=project_key)
        self._cell_writer = WorksheetCellWriter(self.ws, self._logger)
        self._creditor_locator = CreditorBlockLocator()

    def load_all_data(self):
        all_rows = self.ws.get_all_values(include_tailing_empty=False)
        return {
            "column_b_values": [row[1] if len(row) > 1 else "" for row in all_rows],
            "column_c_values": [row[2] if len(row) > 2 else "" for row in all_rows],
            "dates_row": all_rows[4] if len(all_rows) > 4 else [],
            "all_rows": all_rows,
        }

    def get_chapters(self, chapter_codes=None, chapter_names=None):
        chapter_codes = chapter_codes or self.ws.get_col(2, include_tailing_empty=False)
        chapter_names = chapter_names or self.ws.get_col(3, include_tailing_empty=False)

        chapters = {}
        pattern = re.compile(r"^Р\d{1}$")
        for i, code in enumerate(chapter_codes):
            if pattern.match(code) and i < len(chapter_names):
                chapters[code] = chapter_names[i].split(":", 1)[-1].strip() if ":" in chapter_names[i] else chapter_names[i]
        return chapters

    def get_coming(self):
        coming_codes = self.ws.get_col(2, include_tailing_empty=False)
        coming_names = self.ws.get_col(3, include_tailing_empty=False)

        coming = {}
        pattern = re.compile(r"^П$")
        for i, code in enumerate(coming_codes):
            if pattern.match(code) and i < len(coming_names):
                coming[code] = coming_names[i].split(":", 1)[-1].strip() if ":" in coming_names[i] else coming_names[i]
        return coming

    def get_chapter_name(self, chapter_code, chapter_codes=None, chapter_names=None):
        chapters = self.get_chapters(chapter_codes, chapter_names)
        return chapters.get(chapter_code)

    def get_categories(self, chapter_code, codes=None, names=None):
        codes = codes or self.ws.get_col(2, include_tailing_empty=False)
        names = names or self.ws.get_col(3, include_tailing_empty=False)

        start_index = codes.index(chapter_code) + 1
        categories = {}
        for i in range(start_index, len(codes)):
            if codes[i].startswith("Итого"):
                break
            if "." not in codes[i]:
                categories[codes[i]] = names[i]
        return categories

    def get_category_name(self, chapter_code, category_code, codes=None, names=None):
        codes = codes or self.ws.get_col(2, include_tailing_empty=False)
        names = names or self.ws.get_col(3, include_tailing_empty=False)

        start_index = codes.index(chapter_code) + 1
        for i in range(start_index, len(codes)):
            if codes[i].startswith("Итого"):
                break
            if codes[i] == category_code:
                return names[i]
        return ""

    def get_subcategories(self, section_code, category_code, codes=None, names=None):
        codes = codes or self.ws.get_col(2, include_tailing_empty=False)
        names = names or self.ws.get_col(3, include_tailing_empty=False)

        full_category_code = f"{category_code}"
        subcategories = {}
        section_found = False
        category_found = False

        for i, code in enumerate(codes):
            if code == section_code:
                section_found = True
                continue
            if section_found and code == full_category_code:
                category_found = True
                continue

            pattern = re.compile(r"^Р\d{1}$")
            if section_found and (code == "Итого" or (pattern.match(code) and code != full_category_code)):
                break

            if category_found and code.startswith(full_category_code + "."):
                subcategory_code = code[len(full_category_code) + 1:]
                if subcategory_code.isdigit():
                    subcategories[code] = names[i]
        return subcategories

    def get_subcategory_name(self, chapter_code, category_code, subcategory_code, codes=None, names=None):
        codes = codes or self.ws.get_col(2, include_tailing_empty=False)
        names = names or self.ws.get_col(3, include_tailing_empty=False)

        section_found = False
        category_found = False
        for i, code in enumerate(codes):
            if code == chapter_code:
                section_found = True
                continue
            if section_found and code == category_code:
                category_found = True
                continue
            if section_found and (code == "Итого" or code.startswith("Р")):
                break
            if category_found and code == subcategory_code:
                return names[i]
        return ""

    def find_column_by_date(self, date, dates_row=None):
        dates_row = dates_row or self.ws.get_row(5, include_tailing_empty=False)
        for col_index, cell_date in enumerate(dates_row):
            if cell_date == date:
                return col_index + 1
        return None

    def find_row_by_type(self, section_code, type_code, all_codes=None):
        all_codes = all_codes or self.ws.get_col(2, include_tailing_empty=False)
        try:
            section_start = all_codes.index(section_code) + 1
        except ValueError as exc:
            raise ValueError(f"Раздел с кодом {section_code} не найден.") from exc

        try:
            section_end = all_codes.index("Итого", section_start)
        except ValueError:
            section_end = len(all_codes)

        for i in range(section_start, section_end):
            if all_codes[i] == type_code:
                return i + 1
        raise ValueError(f"Тип с кодом {type_code} не найден в разделе {section_code}.")

    def update_cell_with_comment(self, row_index, column_index, amount, comment):
        self._cell_writer.append(row_index, column_index, amount, comment)

    def update_expense_with_comment(self, chapter_code, category_code, date, amount, comment, all_codes=None, names=None, dates_row=None):
        column_index = self.find_column_by_date(date, dates_row)
        if column_index is None:
            raise ValueError(f"Столбец с датой {date} не найден.")

        row_index = self.find_row_by_type(chapter_code, category_code, all_codes)
        self.update_cell_with_comment(row_index, column_index, amount, comment)
        self._logger.info(
            f"Расход добавлен: chapter={chapter_code} category={category_code} date={date} amount={amount} comment={comment}"
        )

    def remove_expense(self, chapter_code, category_code, date, amount, comment, all_codes=None, dates_row=None):
        column_index = self.find_column_by_date(date, dates_row)
        if column_index is None:
            raise ValueError(f"Столбец с датой {date} не найден.")
        row_index = self.find_row_by_type(chapter_code, category_code, all_codes)
        self._cell_writer.clear(row_index, column_index)
        self._logger.info(
            f"Расход удален: chapter={chapter_code} category={category_code} date={date} amount={amount} comment={comment}"
        )

    def update_coming_with_comment(self, chapter_code, coming_code, date, amount, comment, all_codes=None, dates_row=None):
        column_index = self.find_column_by_date(date, dates_row)
        if column_index is None:
            raise ValueError(f"Столбец с датой {date} не найден.")
        row_index = self.find_row_by_type(chapter_code, coming_code, all_codes)
        self.update_cell_with_comment(row_index, column_index, amount, comment)
        self._logger.info(
            f"Приход добавлен: chapter={chapter_code} category={coming_code} date={date} amount={amount} comment={comment}"
        )

    def remove_coming(self, chapter_code, category_code, date, amount, comment, all_codes=None, dates_row=None):
        column_index = self.find_column_by_date(date, dates_row)
        if column_index is None:
            raise ValueError(f"Столбец с датой {date} не найден.")
        row_index = self.find_row_by_type(chapter_code, category_code, all_codes)
        self._cell_writer.clear(row_index, column_index)
        self._logger.info(
            f"Приход удален: chapter={chapter_code} category={category_code} date={date} amount={amount} comment={comment}"
        )

    def get_all_creditors(self, column_b_values=None, column_c_values=None):
        column_b_values = column_b_values or self.ws.get_col(2, include_tailing_empty=False)
        column_c_values = column_c_values or self.ws.get_col(3, include_tailing_empty=False)
        return self._creditor_locator.get_all_creditors(column_b_values, column_c_values)

    def find_credit_info(self, creditor_name, column_b_values=None, column_c_values=None):
        column_b_values = column_b_values or self.ws.get_col(2, include_tailing_empty=False)
        column_c_values = column_c_values or self.ws.get_col(3, include_tailing_empty=False)
        return self._creditor_locator.find_credit_info(creditor_name, column_b_values, column_c_values)

    def record_borrowing(self, creditor, date, amount, comment, all_codes=None, names=None, dates_row=None):
        credit_info = self.find_credit_info(creditor, all_codes, names)
        column_index = self.find_column_by_date(date, dates_row)
        self.update_cell_with_comment(credit_info.borrowing_row, column_index, amount, comment)

    def remove_borrowing(self, creditor, date, amount, comment):
        credit_info = self.find_credit_info(creditor)
        column_index = self.find_column_by_date(date)
        self._cell_writer.clear(credit_info.borrowing_row, column_index)

    def record_saving(self, creditor, date, amount, comment, all_codes=None, names=None, dates_row=None):
        credit_info = self.find_credit_info(creditor, all_codes, names)
        column_index = self.find_column_by_date(date, dates_row)
        self.update_cell_with_comment(credit_info.saving_row, column_index, amount, comment)

    def remove_saving(self, creditor, date, amount, comment):
        credit_info = self.find_credit_info(creditor)
        column_index = self.find_column_by_date(date)
        self._cell_writer.clear(credit_info.saving_row, column_index)

    def record_repayment(self, creditor, date, amount, comment, all_codes=None, names=None, dates_row=None):
        credit_info = self.find_credit_info(creditor, all_codes, names)
        column_index = self.find_column_by_date(date, dates_row)
        self.update_cell_with_comment(credit_info.repayment_row, column_index, amount, comment)

    def remove_repayment(self, creditor, date, amount, comment):
        credit_info = self.find_credit_info(creditor)
        column_index = self.find_column_by_date(date)
        self._cell_writer.clear(credit_info.repayment_row, column_index)
