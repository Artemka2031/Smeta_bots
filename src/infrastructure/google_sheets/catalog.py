from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class SheetsCatalogSnapshot:
    codes: list[str]
    names: list[str]
    dates: list[str]

    def to_state_payload(self) -> dict[str, list[str]]:
        return {
            "column_b_values": self.codes,
            "column_c_values": self.names,
            "dates_row": self.dates,
        }
