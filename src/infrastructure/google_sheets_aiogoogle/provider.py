from __future__ import annotations

import asyncio
import json
from contextlib import asynccontextmanager
from typing import Any

from aiogoogle import Aiogoogle
from aiogoogle.auth.creds import ServiceAccountCreds


class AiogoogleProvider:
    def __init__(
        self,
        service_account_json: str,
        scopes: list[str] | None = None,
    ) -> None:
        if not service_account_json:
            raise ValueError("Google service account credentials are required")

        self._service_account_json = service_account_json
        self._scopes = scopes or ["https://www.googleapis.com/auth/spreadsheets"]
        self._aiogoogle: Aiogoogle | None = None
        self._sheets_api = None
        self._client_lock = asyncio.Lock()
        self._discovery_lock = asyncio.Lock()

    def _build_service_account_creds(self) -> ServiceAccountCreds:
        payload = json.loads(self._service_account_json)
        return ServiceAccountCreds(scopes=self._scopes, **payload)

    async def get_aiogoogle(self) -> Aiogoogle:
        if self._aiogoogle is not None:
            return self._aiogoogle

        async with self._client_lock:
            if self._aiogoogle is None:
                self._aiogoogle = Aiogoogle(service_account_creds=self._build_service_account_creds())
        return self._aiogoogle

    async def get_sheets_api(self):
        if self._sheets_api is not None:
            return self._sheets_api

        async with self._discovery_lock:
            if self._sheets_api is None:
                aiogoogle = await self.get_aiogoogle()
                async with aiogoogle:
                    self._sheets_api = await aiogoogle.discover("sheets", "v4")
        return self._sheets_api

    @asynccontextmanager
    async def session(self):
        aiogoogle = await self.get_aiogoogle()
        async with aiogoogle:
            yield aiogoogle

    async def as_service_account(self, *requests: Any, **kwargs: Any) -> Any:
        async with self.session() as aiogoogle:
            return await aiogoogle.as_service_account(*requests, **kwargs)
