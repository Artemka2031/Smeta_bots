from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class ProjectCatalogSnapshot:
    codes: list[str]
    names: list[str]
    dates: list[str]
