from __future__ import annotations

from typing import Any, Protocol


class SheetsGateway(Protocol):
    async def load_catalog_snapshot(self, force_refresh: bool = False) -> Any: ...

    async def get_chapters(self) -> dict[str, str]: ...

    async def get_coming(self) -> dict[str, str]: ...

    async def get_chapter_name(self, chapter_code: str) -> str | None: ...

    async def get_categories(self, chapter_code: str) -> dict[str, str]: ...

    async def get_category_name(self, chapter_code: str, category_code: str) -> str: ...

    async def get_subcategories(self, chapter_code: str, category_code: str) -> dict[str, str]: ...

    async def get_subcategory_name(
        self,
        chapter_code: str,
        category_code: str,
        subcategory_code: str,
    ) -> str: ...

    async def get_all_creditors(self) -> list[str]: ...

    async def update_expense_with_comment(
        self,
        chapter_code: str,
        category_code: str,
        date: str,
        amount: Any,
        comment: str | None,
    ) -> None: ...

    async def remove_expense(
        self,
        chapter_code: str,
        category_code: str,
        date: str,
        amount: Any,
        comment: str | None,
    ) -> None: ...

    async def update_coming_with_comment(
        self,
        chapter_code: str,
        coming_code: str,
        date: str,
        amount: Any,
        comment: str | None,
    ) -> None: ...

    async def remove_coming(
        self,
        chapter_code: str,
        coming_code: str,
        date: str,
        amount: Any,
        comment: str | None,
    ) -> None: ...

    async def record_borrowing(
        self,
        creditor: str,
        date: str,
        amount: Any,
        comment: str | None,
    ) -> None: ...

    async def remove_borrowing(
        self,
        creditor: str,
        date: str,
        amount: Any,
        comment: str | None,
    ) -> None: ...

    async def record_saving(
        self,
        creditor: str,
        date: str,
        amount: Any,
        comment: str | None,
    ) -> None: ...

    async def remove_saving(
        self,
        creditor: str,
        date: str,
        amount: Any,
        comment: str | None,
    ) -> None: ...

    async def record_repayment(
        self,
        creditor: str,
        date: str,
        amount: Any,
        comment: str | None,
    ) -> None: ...

    async def remove_repayment(
        self,
        creditor: str,
        date: str,
        amount: Any,
        comment: str | None,
    ) -> None: ...
