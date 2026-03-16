from __future__ import annotations

from decimal import Decimal, InvalidOperation


class WorksheetCellWriter:
    def __init__(self, worksheet, logger) -> None:
        self._worksheet = worksheet
        self._logger = logger

    @staticmethod
    def _normalize_comment(comment: str | None) -> str:
        return (comment or "").strip()

    @staticmethod
    def _parse_amount(value: str | int | float | Decimal | None) -> Decimal:
        if value is None:
            return Decimal("0")
        if isinstance(value, Decimal):
            return value
        if isinstance(value, (int, float)):
            return Decimal(str(value))

        normalized = str(value).replace("\xa0", "").replace(" ", "").replace(",", ".").replace("₽", "").strip()
        if not normalized:
            return Decimal("0")
        try:
            return Decimal(normalized)
        except InvalidOperation as exc:
            raise ValueError(f"Не удалось распарсить значение ячейки '{value}'") from exc

    @classmethod
    def _build_note_history(cls, current_note: str | None, comment: str | None) -> str:
        chunks = [chunk.strip() for chunk in (current_note or "").split("\n\n") if chunk.strip()]
        normalized_comment = cls._normalize_comment(comment)
        if normalized_comment:
            chunks.append(normalized_comment)
        return "\n\n".join(chunks)

    def _update_value_only(self, row_index: int, column_index: int, value: Decimal | None) -> None:
        cell = self._worksheet.cell((row_index, column_index))
        cell._value = float(value) if value is not None else ""
        self._worksheet.update_cells([cell], fields="userEnteredValue")

    def _update_note_only(self, row_index: int, column_index: int, note: str) -> None:
        cell = self._worksheet.cell((row_index, column_index))
        cell._note = note
        self._worksheet.update_cells([cell], fields="note")

    def append(self, row_index: int, column_index: int, amount: str | int | float | Decimal, comment: str | None) -> None:
        cell = self._worksheet.cell((row_index, column_index))
        amount_value = self._parse_amount(amount)
        current_amount = self._parse_amount(cell.value)
        new_amount = current_amount + amount_value
        note_history = self._build_note_history(cell.note, comment)

        self._update_value_only(row_index, column_index, new_amount)
        self._update_note_only(row_index, column_index, note_history)

        self._logger.info(
            f"Обновление ячейки: row={row_index} col={column_index} amount={new_amount} comment={comment}"
        )

    def clear(self, row_index: int, column_index: int) -> None:
        self._update_value_only(row_index, column_index, None)
        self._update_note_only(row_index, column_index, "")

        self._logger.info(f"Очистка ячейки: row={row_index} col={column_index}")
