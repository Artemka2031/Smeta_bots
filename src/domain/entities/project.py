from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class Project:
    project_key: str
    name: str
    bot_token: str
    spreadsheet_url: str
    enabled: bool
    id: int | None = None
