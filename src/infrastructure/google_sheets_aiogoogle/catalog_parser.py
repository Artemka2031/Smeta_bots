from __future__ import annotations

import re

from .creditor_locator import CreditorBlockLocator


class SheetsCatalogParser:
    def __init__(self, creditor_locator: CreditorBlockLocator | None = None) -> None:
        self._creditor_locator = creditor_locator or CreditorBlockLocator()
        self._chapter_pattern = re.compile(r"^Р\d{1}$")
        self._coming_pattern = re.compile(r"^П$")

    def get_chapters(self, codes: list[str], names: list[str]) -> dict[str, str]:
        chapters: dict[str, str] = {}
        for index, code in enumerate(codes):
            if not self._chapter_pattern.match(code) or index >= len(names):
                continue
            chapter_name = names[index]
            chapters[code] = chapter_name.split(":", 1)[-1].strip() if ":" in chapter_name else chapter_name
        return chapters

    def get_coming(self, codes: list[str], names: list[str]) -> dict[str, str]:
        coming: dict[str, str] = {}
        for index, code in enumerate(codes):
            if not self._coming_pattern.match(code) or index >= len(names):
                continue
            coming_name = names[index]
            coming[code] = coming_name.split(":", 1)[-1].strip() if ":" in coming_name else coming_name
        return coming

    def get_chapter_name(self, chapter_code: str, codes: list[str], names: list[str]) -> str | None:
        return self.get_chapters(codes, names).get(chapter_code)

    def get_categories(self, chapter_code: str, codes: list[str], names: list[str]) -> dict[str, str]:
        start_index = codes.index(chapter_code) + 1
        categories: dict[str, str] = {}
        for index in range(start_index, len(codes)):
            code = codes[index]
            if code.startswith("Итого"):
                break
            if "." not in code:
                categories[code] = names[index]
        return categories

    def get_category_name(self, chapter_code: str, category_code: str, codes: list[str], names: list[str]) -> str:
        start_index = codes.index(chapter_code) + 1
        for index in range(start_index, len(codes)):
            code = codes[index]
            if code.startswith("Итого"):
                break
            if code == category_code:
                return names[index]
        return ""

    def get_subcategories(
        self,
        chapter_code: str,
        category_code: str,
        codes: list[str],
        names: list[str],
    ) -> dict[str, str]:
        subcategories: dict[str, str] = {}
        section_found = False
        category_found = False

        for index, code in enumerate(codes):
            if code == chapter_code:
                section_found = True
                continue
            if section_found and code == category_code:
                category_found = True
                continue

            if section_found and (code == "Итого" or (self._chapter_pattern.match(code) and code != category_code)):
                break

            if category_found and code.startswith(category_code + "."):
                subcategory_code = code[len(category_code) + 1 :]
                if subcategory_code.isdigit():
                    subcategories[code] = names[index]
        return subcategories

    def get_subcategory_name(
        self,
        chapter_code: str,
        category_code: str,
        subcategory_code: str,
        codes: list[str],
        names: list[str],
    ) -> str:
        section_found = False
        category_found = False

        for index, code in enumerate(codes):
            if code == chapter_code:
                section_found = True
                continue
            if section_found and code == category_code:
                category_found = True
                continue
            if section_found and (code == "Итого" or code.startswith("Р")):
                break
            if category_found and code == subcategory_code:
                return names[index]
        return ""

    def get_all_creditors(self, codes: list[str], names: list[str]) -> list[str]:
        return self._creditor_locator.get_all_creditors(codes, names)
