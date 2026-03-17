from __future__ import annotations

from typing import Any

from src.management.logging import get_logger

from .context import SpreadsheetContext
from .models import CellAddress, SheetRange
from .provider import AiogoogleProvider


class AiogoogleSheetsClient:
    def __init__(
        self,
        spreadsheet_url: str,
        service_account_json: str,
        project_key: str | None = None,
        worksheet_title: str = "Общая таблица",
    ) -> None:
        self._provider = AiogoogleProvider(service_account_json)
        self._context = SpreadsheetContext.from_url(spreadsheet_url, worksheet_title=worksheet_title)
        self._logger = get_logger("aiogoogle-sheets", color="yellow", project_key=project_key)

    @property
    def spreadsheet_id(self) -> str:
        return self._context.spreadsheet_id

    @property
    def worksheet_title(self) -> str:
        return self._context.worksheet_title

    @property
    def worksheet_id(self) -> int | None:
        return self._context.worksheet_id

    @property
    def logger(self):
        return self._logger

    async def ensure_context(self) -> SpreadsheetContext:
        if self._context.worksheet_id is not None:
            return self._context

        sheets_api = await self._provider.get_sheets_api()
        request = sheets_api.spreadsheets.get(
            spreadsheetId=self._context.spreadsheet_id,
            fields="sheets(properties(sheetId,title))",
        )
        response = await self._provider.as_service_account(request)

        for sheet in response.get("sheets", []):
            properties = sheet.get("properties", {})
            if properties.get("title") == self._context.worksheet_title:
                self._context = self._context.with_worksheet_id(properties["sheetId"])
                self._logger.info(
                    f"Resolved worksheet context: title={self._context.worksheet_title} id={self._context.worksheet_id}"
                )
                return self._context

        raise ValueError(f"Worksheet '{self._context.worksheet_title}' not found in spreadsheet")

    async def batch_get_values(self, ranges: list[SheetRange | str], major_dimension: str = "ROWS") -> dict[str, Any]:
        normalized_ranges = [
            item.a1_notation if isinstance(item, SheetRange) else item
            for item in ranges
        ]
        sheets_api = await self._provider.get_sheets_api()
        request = sheets_api.spreadsheets.values.batchGet(
            spreadsheetId=self._context.spreadsheet_id,
            ranges=normalized_ranges,
            majorDimension=major_dimension,
        )
        return await self._provider.as_service_account(request)

    async def get_spreadsheet_grid(
        self,
        ranges: list[SheetRange | str],
        fields: str,
    ) -> dict[str, Any]:
        normalized_ranges = [
            item.a1_notation if isinstance(item, SheetRange) else item
            for item in ranges
        ]
        sheets_api = await self._provider.get_sheets_api()
        request = sheets_api.spreadsheets.get(
            spreadsheetId=self._context.spreadsheet_id,
            ranges=normalized_ranges,
            includeGridData=True,
            fields=fields,
        )
        return await self._provider.as_service_account(request)

    async def batch_update(self, requests: list[dict[str, Any]]) -> dict[str, Any]:
        sheets_api = await self._provider.get_sheets_api()
        request = sheets_api.spreadsheets.batchUpdate(
            spreadsheetId=self._context.spreadsheet_id,
            json={"requests": requests},
        )
        return await self._provider.as_service_account(request)

    async def clear_values(self, ranges: list[str]) -> dict[str, Any]:
        sheets_api = await self._provider.get_sheets_api()
        request = sheets_api.spreadsheets.values.batchClear(
            spreadsheetId=self._context.spreadsheet_id,
            json={"ranges": ranges},
        )
        return await self._provider.as_service_account(request)

    async def build_cell_grid_range(self, address: CellAddress) -> dict[str, int]:
        context = await self.ensure_context()
        if context.worksheet_id is None:
            raise ValueError("Worksheet id must be resolved before building a grid range")

        return {
            "sheetId": context.worksheet_id,
            "startRowIndex": address.row_index - 1,
            "endRowIndex": address.row_index,
            "startColumnIndex": address.column_index - 1,
            "endColumnIndex": address.column_index,
        }
