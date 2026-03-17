from __future__ import annotations

from .models import CellAddress
from .creditor_locator import CreditorBlockLocator, CreditorRowMap


class AiogoogleSheetLocator:
    def __init__(self, worksheet_title: str, creditor_locator: CreditorBlockLocator | None = None) -> None:
        self._worksheet_title = worksheet_title
        self._creditor_locator = creditor_locator or CreditorBlockLocator()

    def find_column_by_date(self, date: str, dates_row: list[str]) -> int:
        for column_index, cell_date in enumerate(dates_row):
            if cell_date == date:
                return column_index + 1
        raise ValueError(f"Столбец с датой {date} не найден.")

    def find_row_by_type(self, section_code: str, type_code: str, all_codes: list[str]) -> int:
        try:
            section_start = all_codes.index(section_code) + 1
        except ValueError as exc:
            raise ValueError(f"Раздел с кодом {section_code} не найден.") from exc

        try:
            section_end = all_codes.index("Итого", section_start)
        except ValueError:
            section_end = len(all_codes)

        for index in range(section_start, section_end):
            if all_codes[index] == type_code:
                return index + 1
        raise ValueError(f"Тип с кодом {type_code} не найден в разделе {section_code}.")

    def find_credit_info(
        self,
        creditor_name: str,
        codes: list[str],
        names: list[str],
    ) -> CreditorRowMap:
        return self._creditor_locator.find_credit_info(creditor_name, codes, names)

    def build_address(self, row_index: int, column_index: int) -> CellAddress:
        return CellAddress(
            row_index=row_index,
            column_index=column_index,
            sheet_title=self._worksheet_title,
        )
