from __future__ import annotations

from decimal import Decimal, InvalidOperation


def normalize_comment(comment: str | None) -> str:
    return (comment or "").strip()


def parse_amount(value: str | int | float | Decimal | None) -> Decimal:
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


def build_note_history(current_note: str | None, comment: str | None) -> str:
    chunks = [chunk.strip() for chunk in (current_note or "").split("\n\n") if chunk.strip()]
    normalized_comment = normalize_comment(comment)
    if normalized_comment:
        chunks.append(normalized_comment)
    return "\n\n".join(chunks)
