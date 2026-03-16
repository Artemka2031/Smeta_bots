from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP


_MONEY_PRECISION = Decimal("0.01")


@dataclass(slots=True, frozen=True)
class BorrowingBreakdown:
    borrowing_amount: Decimal
    saving_amount: Decimal


def calculate_borrowing_breakdown(amount: Decimal, coefficient: Decimal) -> BorrowingBreakdown:
    borrowing_amount = (amount * coefficient).quantize(_MONEY_PRECISION, rounding=ROUND_HALF_UP)
    saving_amount = (amount * (Decimal("1") - coefficient)).quantize(_MONEY_PRECISION, rounding=ROUND_HALF_UP)
    return BorrowingBreakdown(
        borrowing_amount=borrowing_amount,
        saving_amount=max(saving_amount, Decimal("0.00")),
    )
