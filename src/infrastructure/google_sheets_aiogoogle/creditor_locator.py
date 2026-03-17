from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class CreditorRowMap:
    repayment_row: int
    borrowing_row: int
    saving_row: int


class CreditorBlockLocator:
    def __init__(
        self,
        *,
        block_start_marker: str = "К",
        block_end_marker: str = "Итоговая сумма экономии :",
        block_size: int = 5,
        repayment_offset: int = 2,
        borrowing_offset: int = 1,
        saving_offset: int = 3,
    ) -> None:
        self._block_start_marker = block_start_marker
        self._block_end_marker = block_end_marker
        self._block_size = block_size
        self._repayment_offset = repayment_offset
        self._borrowing_offset = borrowing_offset
        self._saving_offset = saving_offset

    def _get_block_bounds(self, column_b_values: list[str]) -> tuple[int, int]:
        try:
            start_index = column_b_values.index(self._block_start_marker) + 1
        except ValueError as exc:
            raise ValueError("Блок кредитов не найден") from exc

        try:
            end_index = column_b_values.index(self._block_end_marker, start_index)
        except ValueError:
            end_index = len(column_b_values)

        return start_index, end_index

    def iter_creditors(self, column_b_values: list[str], column_c_values: list[str]) -> list[tuple[int, str]]:
        start_index, end_index = self._get_block_bounds(column_b_values)
        creditors: list[tuple[int, str]] = []

        for index in range(start_index, end_index):
            creditor = column_c_values[index].strip() if index < len(column_c_values) else ""
            if creditor and (index - start_index) % self._block_size == 0:
                creditors.append((index, creditor))

        return creditors

    def get_all_creditors(self, column_b_values: list[str], column_c_values: list[str]) -> list[str]:
        return [creditor for _, creditor in self.iter_creditors(column_b_values, column_c_values)]

    def find_credit_info(self, creditor_name: str, column_b_values: list[str], column_c_values: list[str]) -> CreditorRowMap:
        for creditor_index, creditor in self.iter_creditors(column_b_values, column_c_values):
            if creditor != creditor_name:
                continue

            return CreditorRowMap(
                repayment_row=creditor_index + self._repayment_offset + 1,
                borrowing_row=creditor_index + self._borrowing_offset + 1,
                saving_row=creditor_index + self._saving_offset + 1,
            )

        raise ValueError(f"Кредитор '{creditor_name}' не найден")
