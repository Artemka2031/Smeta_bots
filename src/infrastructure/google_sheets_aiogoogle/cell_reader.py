from __future__ import annotations

from .client import AiogoogleSheetsClient
from .models import CellAddress, CellSnapshot


class AiogoogleCellReader:
    def __init__(self, client: AiogoogleSheetsClient) -> None:
        self._client = client

    async def read_cells(self, addresses: list[CellAddress]) -> list[CellSnapshot]:
        if not addresses:
            return []

        response = await self._client.get_spreadsheet_grid(
            [address.a1_notation for address in addresses],
            fields=(
                "sheets(data(rowData(values(effectiveValue,formattedValue,note))))"
            ),
        )

        sheets = response.get("sheets", [])
        if not sheets:
            return [CellSnapshot(address=address) for address in addresses]

        data_entries = sheets[0].get("data", [])
        snapshots: list[CellSnapshot] = []
        for index, address in enumerate(addresses):
            cell_payload = self._extract_cell_payload(data_entries, index)
            snapshots.append(
                CellSnapshot(
                    address=address,
                    value=self._extract_value(cell_payload),
                    note=cell_payload.get("note") if cell_payload else None,
                )
            )
        return snapshots

    @staticmethod
    def _extract_cell_payload(data_entries: list[dict], index: int) -> dict:
        if index >= len(data_entries):
            return {}
        row_data = data_entries[index].get("rowData", [])
        if not row_data:
            return {}
        values = row_data[0].get("values", [])
        if not values:
            return {}
        return values[0]

    @staticmethod
    def _extract_value(cell_payload: dict) -> object | None:
        if not cell_payload:
            return None

        effective_value = cell_payload.get("effectiveValue", {})
        if "numberValue" in effective_value:
            return effective_value["numberValue"]
        if "stringValue" in effective_value:
            return effective_value["stringValue"]
        if "boolValue" in effective_value:
            return effective_value["boolValue"]
        return cell_payload.get("formattedValue")
