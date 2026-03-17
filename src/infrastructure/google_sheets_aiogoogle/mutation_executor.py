from __future__ import annotations

from decimal import Decimal

from .client import AiogoogleSheetsClient
from .models import CellAddress, CellMutation, CellSnapshot
from .mutation_utils import build_note_history, parse_amount


class AiogoogleMutationExecutor:
    def __init__(self, client: AiogoogleSheetsClient, logger) -> None:
        self._client = client
        self._logger = logger

    async def append(self, snapshot: CellSnapshot, amount: str | int | float | Decimal, comment: str | None) -> None:
        amount_value = parse_amount(amount)
        current_amount = parse_amount(snapshot.value)
        new_amount = current_amount + amount_value
        note_history = build_note_history(snapshot.note, comment)

        await self.apply_mutations(
            [
                CellMutation(
                    address=snapshot.address,
                    value=new_amount,
                    note=note_history,
                )
            ]
        )

        self._logger.info(
            f"Обновление ячейки: row={snapshot.address.row_index} col={snapshot.address.column_index} amount={new_amount} comment={comment}"
        )

    async def clear(self, address: CellAddress) -> None:
        await self._client.clear_values([address.a1_notation])
        await self.apply_mutations(
            [
                CellMutation(
                    address=address,
                    clear_note=True,
                )
            ]
        )
        self._logger.info(f"Очистка ячейки: row={address.row_index} col={address.column_index}")

    async def apply_mutations(self, mutations: list[CellMutation]) -> None:
        requests: list[dict] = []
        for mutation in mutations:
            requests.append(await self._build_repeat_cell_request(mutation))
        if requests:
            await self._client.batch_update(requests)

    async def _build_repeat_cell_request(self, mutation: CellMutation) -> dict:
        grid_range = await self._client.build_cell_grid_range(mutation.address)
        cell_payload: dict[str, object] = {}
        field_names: list[str] = []

        if mutation.clear_note:
            cell_payload["note"] = ""
            field_names.append("note")
        elif mutation.note is not None:
            cell_payload["note"] = mutation.note
            field_names.append("note")

        if mutation.clear_value:
            cell_payload["userEnteredValue"] = {}
            field_names.append("userEnteredValue")
        elif mutation.value is not None:
            cell_payload["userEnteredValue"] = self._serialize_value(mutation.value)
            field_names.append("userEnteredValue")

        return {
            "repeatCell": {
                "range": grid_range,
                "cell": cell_payload,
                "fields": ",".join(field_names),
            }
        }

    @staticmethod
    def _serialize_value(value: object) -> dict[str, object]:
        if isinstance(value, Decimal):
            return {"numberValue": float(value)}
        if isinstance(value, bool):
            return {"boolValue": value}
        if isinstance(value, int):
            return {"numberValue": value}
        if isinstance(value, float):
            return {"numberValue": value}
        return {"stringValue": str(value)}
