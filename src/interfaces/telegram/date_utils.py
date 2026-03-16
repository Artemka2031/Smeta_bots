from __future__ import annotations

from datetime import date, datetime


INPUT_DATE_FORMAT = "%d.%m.%y"
SHEET_DATE_FORMAT = "%d.%m.%Y"


def parse_input_date(value: str) -> date:
    return datetime.strptime(value, INPUT_DATE_FORMAT).date()


def format_input_date(value: date) -> str:
    return value.strftime(INPUT_DATE_FORMAT)


def format_sheet_date(value: date) -> str:
    return value.strftime(SHEET_DATE_FORMAT)
