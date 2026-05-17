"""Async HTTP client for Zipp's public news REST API.

Thin httpx wrapper. Each method maps to one endpoint under
``/api/v1/news/*`` and forwards the raw JSON response — the parent
API and the MCP tool surface share a shape by design, so there's no
translation layer here.

Why no transformation: the wrapper exists to be a drop-in for the
hosted MCP server, not a higher-level SDK. If the parent gains a
field, it appears here automatically and the wrapper does not need
a new release.
"""
from __future__ import annotations

from typing import Any

import httpx

from zipp_mcp import __version__
from zipp_mcp.settings import Settings, get_settings

_USER_AGENT = f"zipp-mcp/{__version__} (+https://github.com/deficlow/zipp-mcp)"
_API_PREFIX = "/api/v1/news"


class ZippAPIError(RuntimeError):
    """Raised when the Zipp REST API returns a non-2xx status.

    Attributes:
        status_code: HTTP status the upstream returned.
        body: Response body text, truncated to 4 KiB for log safety.
    """

    def __init__(self, status_code: int, body: str) -> None:
        super().__init__(f"Zipp API {status_code}: {body[:200]}")
        self.status_code = status_code
        self.body = body[:4096]


class ZippClient:
    """Async client for the Zipp news REST API.

    Use as an async context manager so the underlying httpx connection
    pool is closed cleanly when the calling tool returns. One client
    per tool call is fine — connection pooling is per-event-loop and
    setup cost is negligible compared to the network round-trip.

    Example::

        async with ZippClient() as zipp:
            payload = await zipp.search(query="bitcoin etf", limit=5)
    """

    def __init__(
        self,
        *,
        settings: Settings | None = None,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        cfg = settings or get_settings()
        self._client = httpx.AsyncClient(
            base_url=str(cfg.api_base).rstrip("/"),
            timeout=cfg.api_timeout_s,
            headers={
                "User-Agent": _USER_AGENT,
                "Accept": "application/json",
            },
            transport=transport,
        )

    async def __aenter__(self) -> ZippClient:
        return self

    async def __aexit__(self, *exc: object) -> None:
        await self._client.aclose()

    async def aclose(self) -> None:
        await self._client.aclose()

    # ── Endpoint methods ────────────────────────────────────────────

    async def search(
        self,
        *,
        query: str,
        lang: str = "en-US",
        category: str | None = None,
        limit: int = 10,
    ) -> dict[str, Any]:
        params: dict[str, Any] = {"query": query, "lang": lang, "limit": limit}
        if category:
            params["category"] = category
        return await self._get("/search", params=params)

    async def get_latest(
        self,
        *,
        lang: str = "en-US",
        category: str | None = None,
        limit: int = 10,
    ) -> dict[str, Any]:
        params: dict[str, Any] = {"lang": lang, "limit": limit}
        if category:
            params["category"] = category
        return await self._get("/latest", params=params)

    async def get_breaking(
        self,
        *,
        lang: str = "en-US",
        limit: int = 10,
    ) -> dict[str, Any]:
        return await self._get("/breaking", params={"lang": lang, "limit": limit})

    async def get_featured(
        self,
        *,
        lang: str = "en-US",
        limit: int = 10,
    ) -> dict[str, Any]:
        return await self._get("/featured", params={"lang": lang, "limit": limit})

    async def get_post(
        self,
        *,
        slug_or_id: str,
        lang: str = "en-US",
    ) -> dict[str, Any]:
        # Path encoding is handled by httpx — slugs are URL-safe by
        # construction, numeric ids are ASCII digits.
        return await self._get(f"/posts/{slug_or_id}", params={"lang": lang})

    async def list_categories(
        self,
        *,
        lang: str = "en-US",
    ) -> dict[str, Any]:
        return await self._get("/categories", params={"lang": lang})

    # ── Internals ───────────────────────────────────────────────────

    async def _get(self, path: str, *, params: dict[str, Any]) -> dict[str, Any]:
        # Drop None values so the upstream doesn't get e.g. ?category=None.
        clean = {k: v for k, v in params.items() if v is not None}
        resp = await self._client.get(_API_PREFIX + path, params=clean)
        if resp.status_code >= 400:
            raise ZippAPIError(resp.status_code, resp.text)
        return resp.json()
