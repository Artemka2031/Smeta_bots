from __future__ import annotations

import asyncio
from dataclasses import dataclass
from time import monotonic
from typing import Any

from .catalog import SheetsCatalogSnapshot
from .catalog_parser import SheetsCatalogParser
from .catalog_reader import AiogoogleCatalogReader
from .cell_reader import AiogoogleCellReader
from .client import AiogoogleSheetsClient
from .locator import AiogoogleSheetLocator
from .mutation_executor import AiogoogleMutationExecutor


@dataclass(slots=True)
class _CatalogCacheEntry:
    snapshot: SheetsCatalogSnapshot
    expires_at: float


class AiogoogleSheetsGateway:
    def __init__(self, client: AiogoogleSheetsClient, cache_ttl_seconds: int = 300) -> None:
        self._client = client
        self._cache_ttl_seconds = cache_ttl_seconds
        self._catalog_cache: _CatalogCacheEntry | None = None
        self._catalog_reader = AiogoogleCatalogReader(client)
        self._catalog_parser = SheetsCatalogParser()
        self._cell_reader = AiogoogleCellReader(client)
        self._mutation_executor = AiogoogleMutationExecutor(client, client.logger)
        self._locator = AiogoogleSheetLocator(client.worksheet_title)
        self._write_lock = asyncio.Lock()

    async def _resolve_catalog(
        self,
        codes: list[str] | None = None,
        names: list[str] | None = None,
        dates: list[str] | None = None,
    ) -> tuple[list[str], list[str], list[str]]:
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

        snapshot = await self._catalog_reader.load_snapshot()
        self._catalog_cache = _CatalogCacheEntry(
            snapshot=snapshot,
            expires_at=now + self._cache_ttl_seconds,
        )
        return snapshot

    async def get_chapters(self, codes: list[str] | None = None, names: list[str] | None = None) -> dict[str, str]:
        codes, names, _ = await self._resolve_catalog(codes, names)
        return self._catalog_parser.get_chapters(codes, names)

    async def get_coming(self) -> dict[str, str]:
        snapshot = await self.load_catalog_snapshot()
        return self._catalog_parser.get_coming(snapshot.codes, snapshot.names)

    async def get_chapter_name(
        self,
        chapter_code: str,
        codes: list[str] | None = None,
        names: list[str] | None = None,
    ) -> str | None:
        codes, names, _ = await self._resolve_catalog(codes, names)
        return self._catalog_parser.get_chapter_name(chapter_code, codes, names)

    async def get_categories(
        self,
        chapter_code: str,
        codes: list[str] | None = None,
        names: list[str] | None = None,
    ) -> dict[str, str]:
        codes, names, _ = await self._resolve_catalog(codes, names)
        return self._catalog_parser.get_categories(chapter_code, codes, names)

    async def get_category_name(
        self,
        chapter_code: str,
        category_code: str,
        codes: list[str] | None = None,
        names: list[str] | None = None,
    ) -> str:
        codes, names, _ = await self._resolve_catalog(codes, names)
        return self._catalog_parser.get_category_name(chapter_code, category_code, codes, names)

    async def get_subcategories(
        self,
        chapter_code: str,
        category_code: str,
        codes: list[str] | None = None,
        names: list[str] | None = None,
    ) -> dict[str, str]:
        codes, names, _ = await self._resolve_catalog(codes, names)
        return self._catalog_parser.get_subcategories(chapter_code, category_code, codes, names)

    async def get_subcategory_name(
        self,
        chapter_code: str,
        category_code: str,
        subcategory_code: str,
        codes: list[str] | None = None,
        names: list[str] | None = None,
    ) -> str:
        codes, names, _ = await self._resolve_catalog(codes, names)
        return self._catalog_parser.get_subcategory_name(
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
        return self._catalog_parser.get_all_creditors(codes, names)

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
        codes, _, dates = await self._resolve_catalog(codes, names, dates)
        row_index = self._locator.find_row_by_type(chapter_code, category_code, codes)
        column_index = self._locator.find_column_by_date(date, dates)
        await self._append_to_cell(self._locator.build_address(row_index, column_index), amount, comment)

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
        row_index = self._locator.find_row_by_type(chapter_code, category_code, codes)
        column_index = self._locator.find_column_by_date(date, dates)
        await self._clear_cell(self._locator.build_address(row_index, column_index))

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
        row_index = self._locator.find_row_by_type(chapter_code, coming_code, codes)
        column_index = self._locator.find_column_by_date(date, dates)
        await self._append_to_cell(self._locator.build_address(row_index, column_index), amount, comment)

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
        row_index = self._locator.find_row_by_type(chapter_code, coming_code, codes)
        column_index = self._locator.find_column_by_date(date, dates)
        await self._clear_cell(self._locator.build_address(row_index, column_index))

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
        credit_info = self._locator.find_credit_info(creditor, codes, names)
        column_index = self._locator.find_column_by_date(date, dates)
        await self._append_to_cell(self._locator.build_address(credit_info.borrowing_row, column_index), amount, comment)

    async def remove_borrowing(self, creditor: str, date: str, amount: Any, comment: str | None) -> None:
        snapshot = await self.load_catalog_snapshot()
        credit_info = self._locator.find_credit_info(creditor, snapshot.codes, snapshot.names)
        column_index = self._locator.find_column_by_date(date, snapshot.dates)
        await self._clear_cell(self._locator.build_address(credit_info.borrowing_row, column_index))

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
        credit_info = self._locator.find_credit_info(creditor, codes, names)
        column_index = self._locator.find_column_by_date(date, dates)
        await self._append_to_cell(self._locator.build_address(credit_info.saving_row, column_index), amount, comment)

    async def remove_saving(self, creditor: str, date: str, amount: Any, comment: str | None) -> None:
        snapshot = await self.load_catalog_snapshot()
        credit_info = self._locator.find_credit_info(creditor, snapshot.codes, snapshot.names)
        column_index = self._locator.find_column_by_date(date, snapshot.dates)
        await self._clear_cell(self._locator.build_address(credit_info.saving_row, column_index))

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
        credit_info = self._locator.find_credit_info(creditor, codes, names)
        column_index = self._locator.find_column_by_date(date, dates)
        await self._append_to_cell(self._locator.build_address(credit_info.repayment_row, column_index), amount, comment)

    async def remove_repayment(self, creditor: str, date: str, amount: Any, comment: str | None) -> None:
        snapshot = await self.load_catalog_snapshot()
        credit_info = self._locator.find_credit_info(creditor, snapshot.codes, snapshot.names)
        column_index = self._locator.find_column_by_date(date, snapshot.dates)
        await self._clear_cell(self._locator.build_address(credit_info.repayment_row, column_index))

    async def _append_to_cell(self, address, amount: Any, comment: str | None) -> None:
        async with self._write_lock:
            snapshot = (await self._cell_reader.read_cells([address]))[0]
            await self._mutation_executor.append(snapshot, amount, comment)

    async def _clear_cell(self, address) -> None:
        async with self._write_lock:
            await self._mutation_executor.clear(address)
