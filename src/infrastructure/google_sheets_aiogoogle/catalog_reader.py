from __future__ import annotations

from .client import AiogoogleSheetsClient
from .catalog import SheetsCatalogSnapshot


class AiogoogleCatalogReader:
    def __init__(self, client: AiogoogleSheetsClient) -> None:
        self._client = client

    async def load_snapshot(self) -> SheetsCatalogSnapshot:
        response = await self._client.batch_get_values(
            [
                f"{self._client.worksheet_title}!B:B",
                f"{self._client.worksheet_title}!C:C",
                f"{self._client.worksheet_title}!5:5",
            ]
        )
        value_ranges = response.get("valueRanges", [])

        column_b = self._normalize_column(value_ranges[0] if len(value_ranges) > 0 else {})
        column_c = self._normalize_column(value_ranges[1] if len(value_ranges) > 1 else {})
        dates = self._normalize_row(value_ranges[2] if len(value_ranges) > 2 else {})

        return SheetsCatalogSnapshot(
            codes=column_b,
            names=column_c,
            dates=dates,
        )

    @staticmethod
    def _normalize_column(value_range: dict) -> list[str]:
        values = value_range.get("values", [])
        if not values:
            return []
        return [row[0] if row else "" for row in values]

    @staticmethod
    def _normalize_row(value_range: dict) -> list[str]:
        values = value_range.get("values", [])
        if not values:
            return []
        return [str(value) for value in values[0]]
