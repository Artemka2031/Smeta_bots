from __future__ import annotations

import re
from dataclasses import dataclass, replace
from urllib.parse import urlparse


_SPREADSHEET_ID_PATTERN = re.compile(r"/spreadsheets/d/([a-zA-Z0-9-_]+)")


@dataclass(slots=True, frozen=True)
class SpreadsheetContext:
    spreadsheet_url: str
    spreadsheet_id: str
    worksheet_title: str = "Общая таблица"
    worksheet_id: int | None = None

    @classmethod
    def from_url(cls, spreadsheet_url: str, worksheet_title: str = "Общая таблица") -> SpreadsheetContext:
        spreadsheet_id = cls.parse_spreadsheet_id(spreadsheet_url)
        return cls(
            spreadsheet_url=spreadsheet_url,
            spreadsheet_id=spreadsheet_id,
            worksheet_title=worksheet_title,
            worksheet_id=None,
        )

    @staticmethod
    def parse_spreadsheet_id(spreadsheet_url: str) -> str:
        parsed = urlparse(spreadsheet_url)
        match = _SPREADSHEET_ID_PATTERN.search(parsed.path)
        if not match:
            raise ValueError(f"Invalid Google Sheets URL: {spreadsheet_url}")
        return match.group(1)

    def with_worksheet_id(self, worksheet_id: int) -> SpreadsheetContext:
        return replace(self, worksheet_id=worksheet_id)
