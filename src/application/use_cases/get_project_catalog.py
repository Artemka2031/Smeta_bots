from __future__ import annotations

from src.application.dto import ProjectCatalogSnapshot
from src.application.gateways import SheetsGateway


class GetProjectCatalog:
    def __init__(self, sheets_gateway: SheetsGateway) -> None:
        self._sheets_gateway = sheets_gateway

    async def preload(self, force_refresh: bool = False) -> ProjectCatalogSnapshot:
        snapshot = await self._sheets_gateway.load_catalog_snapshot(force_refresh=force_refresh)
        return ProjectCatalogSnapshot(
            codes=list(snapshot.codes),
            names=list(snapshot.names),
            dates=list(snapshot.dates),
        )

    async def get_expense_chapters(self) -> dict[str, str]:
        return await self._sheets_gateway.get_chapters()

    async def get_coming_chapters(self) -> dict[str, str]:
        return await self._sheets_gateway.get_coming()

    async def get_categories(self, chapter_code: str) -> dict[str, str]:
        return await self._sheets_gateway.get_categories(chapter_code)

    async def get_subcategories(self, chapter_code: str, category_code: str) -> dict[str, str]:
        return await self._sheets_gateway.get_subcategories(chapter_code, category_code)

    async def get_chapter_name(self, chapter_code: str) -> str | None:
        return await self._sheets_gateway.get_chapter_name(chapter_code)

    async def get_category_name(self, chapter_code: str, category_code: str) -> str:
        return await self._sheets_gateway.get_category_name(chapter_code, category_code)

    async def get_subcategory_name(
        self,
        chapter_code: str,
        category_code: str,
        subcategory_code: str,
    ) -> str:
        return await self._sheets_gateway.get_subcategory_name(
            chapter_code,
            category_code,
            subcategory_code,
        )

    async def get_creditors(self) -> list[str]:
        return await self._sheets_gateway.get_all_creditors()
