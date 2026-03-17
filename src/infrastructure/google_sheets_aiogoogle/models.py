from __future__ import annotations

from dataclasses import dataclass
from typing import Any


def _column_to_letters(column_index: int) -> str:
    if column_index < 1:
        raise ValueError("Column index must be positive")

    letters: list[str] = []
    current = column_index
    while current > 0:
        current, remainder = divmod(current - 1, 26)
        letters.append(chr(65 + remainder))
    return "".join(reversed(letters))


@dataclass(slots=True, frozen=True)
class CellAddress:
    row_index: int
    column_index: int
    sheet_title: str

    @property
    def a1_notation(self) -> str:
        return f"{self.sheet_title}!{_column_to_letters(self.column_index)}{self.row_index}"


@dataclass(slots=True, frozen=True)
class SheetRange:
    sheet_title: str
    start_row: int
    end_row: int | None = None
    start_column: int = 1
    end_column: int | None = None

    @property
    def a1_notation(self) -> str:
        start = f"{_column_to_letters(self.start_column)}{self.start_row}"

        if self.end_row is None and self.end_column is None:
            return f"{self.sheet_title}!{start}"

        end_column = self.end_column or self.start_column
        end_row = self.end_row or self.start_row
        end = f"{_column_to_letters(end_column)}{end_row}"
        return f"{self.sheet_title}!{start}:{end}"


@dataclass(slots=True, frozen=True)
class CellSnapshot:
    address: CellAddress
    value: Any = None
    note: str | None = None


@dataclass(slots=True, frozen=True)
class CellMutation:
    address: CellAddress
    value: Any | None = None
    note: str | None = None
    clear_value: bool = False
    clear_note: bool = False
