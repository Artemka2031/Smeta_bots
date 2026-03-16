from __future__ import annotations

import asyncio
from dataclasses import dataclass
from time import monotonic
from typing import Any

from .client import GoogleSheetsClient
from .catalog import SheetsCatalogSnapshot


@dataclass(slots=True)
class _CatalogCacheEntry:
    snapshot: SheetsCatalogSnapshot
    expires_at: float


class AsyncSheetsGateway:
    def __init__(self, client: GoogleSheetsClient, cache_ttl_seconds: int = 300) -> None:
        self._client = client
        self._cache_ttl_seconds = cache_ttl_seconds
        self._catalog_cache: _CatalogCacheEntry | None = None
        self._write_lock = asyncio.Lock()

    async def _run_write(self, func, *args) -> None:
        async with self._write_lock:
            await asyncio.to_thread(func, *args)

    async def _resolve_catalog(
        self,
        codes: list[str] | None = None,
        names: list[str] | None = None,
        dates: list[str] | None = None,
    ) -> tuple[list[str] | None, list[str] | None, list[str] | None]:
        if codes is not None and names is not None and dates is not None:
            return codes, names, dates

        snapshot = await self.load_catalog_snapshot()
        return (
            codes if codes is not None else snapshot.codes,
            names if names is not None else snapshot.names,
            dates if dates is not None else snapshot.dates,
        )

    async def load_catalog_snapshot(self, force_refresh: bool = False) -> SheetsCatalogSnapshot:
        now = monotonic()
        if not force_refresh and self._catalog_cache and self._catalog_cache.expires_at > now:
            return self._catalog_cache.snapshot

        payload = await asyncio.to_thread(self._client.load_all_data)
        snapshot = SheetsCatalogSnapshot(
            codes=payload["column_b_values"],
            names=payload["column_c_values"],
            dates=payload["dates_row"],
        )
        self._catalog_cache = _CatalogCacheEntry(
            snapshot=snapshot,
            expires_at=now + self._cache_ttl_seconds,
        )
        return snapshot

    async def get_chapters(self, codes: list[str] | None = None, names: list[str] | None = None) -> dict[str, str]:
        codes, names, _ = await self._resolve_catalog(codes, names)
        return await asyncio.to_thread(self._client.get_chapters, codes, names)

    async def get_coming(self) -> dict[str, str]:
        return await asyncio.to_thread(self._client.get_coming)

    async def get_chapter_name(
        self,
        chapter_code: str,
        codes: list[str] | None = None,
        names: list[str] | None = None,
    ) -> str | None:
        codes, names, _ = await self._resolve_catalog(codes, names)
        return await asyncio.to_thread(self._client.get_chapter_name, chapter_code, codes, names)

    async def get_categories(
        self,
        chapter_code: str,
        codes: list[str] | None = None,
        names: list[str] | None = None,
    ) -> dict[str, str]:
        codes, names, _ = await self._resolve_catalog(codes, names)
        return await asyncio.to_thread(self._client.get_categories, chapter_code, codes, names)

    async def get_category_name(
        self,
        chapter_code: str,
        category_code: str,
        codes: list[str] | None = None,
        names: list[str] | None = None,
    ) -> str:
        codes, names, _ = await self._resolve_catalog(codes, names)
        return await asyncio.to_thread(
            self._client.get_category_name,
            chapter_code,
            category_code,
            codes,
            names,
        )

    async def get_subcategories(
        self,
        chapter_code: str,
        category_code: str,
        codes: list[str] | None = None,
        names: list[str] | None = None,
    ) -> dict[str, str]:
        codes, names, _ = await self._resolve_catalog(codes, names)
        return await asyncio.to_thread(
            self._client.get_subcategories,
            chapter_code,
            category_code,
            codes,
            names,
        )

    async def get_subcategory_name(
        self,
        chapter_code: str,
        category_code: str,
        subcategory_code: str,
        codes: list[str] | None = None,
        names: list[str] | None = None,
    ) -> str:
        codes, names, _ = await self._resolve_catalog(codes, names)
        return await asyncio.to_thread(
            self._client.get_subcategory_name,
            chapter_code,
            category_code,
            subcategory_code,
            codes,
            names,
        )

    async def get_all_creditors(
        self,
        codes: list[str] | None = None,
        names: list[str] | None = None,
    ) -> list[str]:
        codes, names, _ = await self._resolve_catalog(codes, names)
        return await asyncio.to_thread(self._client.get_all_creditors, codes, names)

    async def update_expense_with_comment(
        self,
        chapter_code: str,
        category_code: str,
        date: str,
        amount: Any,
        comment: str | None,
        codes: list[str] | None = None,
        names: list[str] | None = None,
        dates: list[str] | None = None,
    ) -> None:
        codes, names, dates = await self._resolve_catalog(codes, names, dates)
        await self._run_write(
            self._client.update_expense_with_comment,
            chapter_code,
            category_code,
            date,
            amount,
            comment,
            codes,
            names,
            dates,
        )

    async def remove_expense(
        self,
        chapter_code: str,
        category_code: str,
        date: str,
        amount: Any,
        comment: str | None,
        codes: list[str] | None = None,
        dates: list[str] | None = None,
    ) -> None:
        codes, _, dates = await self._resolve_catalog(codes, None, dates)
        await self._run_write(
            self._client.remove_expense,
            chapter_code,
            category_code,
            date,
            amount,
            comment,
            codes,
            dates,
        )

    async def update_coming_with_comment(
        self,
        chapter_code: str,
        coming_code: str,
        date: str,
        amount: Any,
        comment: str | None,
        codes: list[str] | None = None,
        dates: list[str] | None = None,
    ) -> None:
        codes, _, dates = await self._resolve_catalog(codes, None, dates)
        await self._run_write(
            self._client.update_coming_with_comment,
            chapter_code,
            coming_code,
            date,
            amount,
            comment,
            codes,
            dates,
        )

    async def remove_coming(
        self,
        chapter_code: str,
        coming_code: str,
        date: str,
        amount: Any,
        comment: str | None,
        codes: list[str] | None = None,
        dates: list[str] | None = None,
    ) -> None:
        codes, _, dates = await self._resolve_catalog(codes, None, dates)
        await self._run_write(
            self._client.remove_coming,
            chapter_code,
            coming_code,
            date,
            amount,
            comment,
            codes,
            dates,
        )

    async def record_borrowing(
        self,
        creditor: str,
        date: str,
        amount: Any,
        comment: str | None,
        codes: list[str] | None = None,
        names: list[str] | None = None,
        dates: list[str] | None = None,
    ) -> None:
        codes, names, dates = await self._resolve_catalog(codes, names, dates)
        await self._run_write(
            self._client.record_borrowing,
            creditor,
            date,
            amount,
            comment,
            codes,
            names,
            dates,
        )

    async def remove_borrowing(
        self,
        creditor: str,
        date: str,
        amount: Any,
        comment: str | None,
    ) -> None:
        await self._run_write(self._client.remove_borrowing, creditor, date, amount, comment)

    async def record_saving(
        self,
        creditor: str,
        date: str,
        amount: Any,
        comment: str | None,
        codes: list[str] | None = None,
        names: list[str] | None = None,
        dates: list[str] | None = None,
    ) -> None:
        codes, names, dates = await self._resolve_catalog(codes, names, dates)
        await self._run_write(
            self._client.record_saving,
            creditor,
            date,
            amount,
            comment,
            codes,
            names,
            dates,
        )

    async def remove_saving(
        self,
        creditor: str,
        date: str,
        amount: Any,
        comment: str | None,
    ) -> None:
        await self._run_write(self._client.remove_saving, creditor, date, amount, comment)

    async def record_repayment(
        self,
        creditor: str,
        date: str,
        amount: Any,
        comment: str | None,
        codes: list[str] | None = None,
        names: list[str] | None = None,
        dates: list[str] | None = None,
    ) -> None:
        codes, names, dates = await self._resolve_catalog(codes, names, dates)
        await self._run_write(
            self._client.record_repayment,
            creditor,
            date,
            amount,
            comment,
            codes,
            names,
            dates,
        )

    async def remove_repayment(
        self,
        creditor: str,
        date: str,
        amount: Any,
        comment: str | None,
    ) -> None:
        await self._run_write(self._client.remove_repayment, creditor, date, amount, comment)
