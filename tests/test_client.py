"""Unit tests for :class:`ZippClient`.

These tests are about *shape* — what path, what query params, what
header — not about whether the upstream returns realistic data. The
parent API's contract is covered by parent-side tests; the wrapper's
job is to forward correctly.
"""
from __future__ import annotations

from urllib.parse import parse_qs

import httpx
import pytest

from tests.conftest import make_transport
from zipp_mcp.client import ZippAPIError, ZippClient
from zipp_mcp.settings import Settings


@pytest.fixture
def settings() -> Settings:
    return Settings(api_base="https://test.invalid", api_timeout_s=5.0)


async def test_search_sends_query_and_optional_category(settings: Settings) -> None:
    seen: list[httpx.Request] = []

    def handler(req: httpx.Request) -> httpx.Response:
        seen.append(req)
        return httpx.Response(200, json={"items": [], "total": 0})

    async with ZippClient(settings=settings, transport=httpx.MockTransport(handler)) as c:
        await c.search(query="bitcoin etf", lang="en-US", category="markets-etfs", limit=5)

    assert len(seen) == 1
    req = seen[0]
    assert req.method == "GET"
    assert req.url.path == "/api/v1/news/search"
    params = parse_qs(str(req.url.query.decode()))
    assert params["query"] == ["bitcoin etf"]
    assert params["lang"] == ["en-US"]
    assert params["category"] == ["markets-etfs"]
    assert params["limit"] == ["5"]


async def test_search_drops_none_category(settings: Settings) -> None:
    seen: list[httpx.Request] = []

    def handler(req: httpx.Request) -> httpx.Response:
        seen.append(req)
        return httpx.Response(200, json={"items": []})

    async with ZippClient(settings=settings, transport=httpx.MockTransport(handler)) as c:
        await c.search(query="bitcoin")

    params = parse_qs(seen[0].url.query.decode())
    assert "category" not in params
    assert params["query"] == ["bitcoin"]


async def test_get_latest_path_and_defaults(settings: Settings) -> None:
    seen: list[httpx.Request] = []

    def handler(req: httpx.Request) -> httpx.Response:
        seen.append(req)
        return httpx.Response(200, json={"items": []})

    async with ZippClient(settings=settings, transport=httpx.MockTransport(handler)) as c:
        await c.get_latest()

    assert seen[0].url.path == "/api/v1/news/latest"
    params = parse_qs(seen[0].url.query.decode())
    assert params["lang"] == ["en-US"]
    assert params["limit"] == ["10"]


async def test_get_breaking_path(settings: Settings) -> None:
    seen: list[httpx.Request] = []

    def handler(req: httpx.Request) -> httpx.Response:
        seen.append(req)
        return httpx.Response(200, json={"items": []})

    async with ZippClient(settings=settings, transport=httpx.MockTransport(handler)) as c:
        await c.get_breaking(lang="tr-TR", limit=3)

    assert seen[0].url.path == "/api/v1/news/breaking"
    params = parse_qs(seen[0].url.query.decode())
    assert params["lang"] == ["tr-TR"]
    assert params["limit"] == ["3"]


async def test_get_featured_path(settings: Settings) -> None:
    seen: list[httpx.Request] = []

    def handler(req: httpx.Request) -> httpx.Response:
        seen.append(req)
        return httpx.Response(200, json={"items": []})

    async with ZippClient(settings=settings, transport=httpx.MockTransport(handler)) as c:
        await c.get_featured()

    assert seen[0].url.path == "/api/v1/news/featured"


async def test_get_post_slug_in_path(settings: Settings) -> None:
    seen: list[httpx.Request] = []

    def handler(req: httpx.Request) -> httpx.Response:
        seen.append(req)
        return httpx.Response(200, json={"item": {}})

    async with ZippClient(settings=settings, transport=httpx.MockTransport(handler)) as c:
        await c.get_post(slug_or_id="bitcoin-etf-inflows-500m", lang="en-US")

    assert seen[0].url.path == "/api/v1/news/posts/bitcoin-etf-inflows-500m"


async def test_list_categories_path(settings: Settings) -> None:
    seen: list[httpx.Request] = []

    def handler(req: httpx.Request) -> httpx.Response:
        seen.append(req)
        return httpx.Response(200, json={"groups": []})

    async with ZippClient(settings=settings, transport=httpx.MockTransport(handler)) as c:
        await c.list_categories()

    assert seen[0].url.path == "/api/v1/news/categories"


async def test_response_json_forwarded_unchanged(settings: Settings) -> None:
    payload = {
        "items": [
            {
                "id": 1234,
                "slug": "btc-etf-inflows",
                "sentiment": "BULLISH",
                "importance": 82,
                "source": {"name": "CoinDesk", "url": "https://example.test"},
            }
        ],
        "total": 1,
    }

    async with ZippClient(
        settings=settings,
        transport=make_transport(payload),
    ) as c:
        got = await c.get_latest()

    assert got == payload


async def test_non_2xx_raises_zipp_api_error(settings: Settings) -> None:
    def handler(req: httpx.Request) -> httpx.Response:
        return httpx.Response(500, text="upstream blew up")

    async with ZippClient(settings=settings, transport=httpx.MockTransport(handler)) as c:
        with pytest.raises(ZippAPIError) as excinfo:
            await c.get_latest()

    assert excinfo.value.status_code == 500
    assert "upstream blew up" in excinfo.value.body


async def test_user_agent_header_set(settings: Settings) -> None:
    seen: list[httpx.Request] = []

    def handler(req: httpx.Request) -> httpx.Response:
        seen.append(req)
        return httpx.Response(200, json={})

    async with ZippClient(settings=settings, transport=httpx.MockTransport(handler)) as c:
        await c.get_latest()

    ua = seen[0].headers.get("user-agent", "")
    assert ua.startswith("zipp-mcp/")
    assert "github.com/deficlow/zipp-mcp" in ua


async def test_base_url_respected(settings: Settings) -> None:
    """If ZIPP_API_BASE points at a custom mirror, the path is still
    appended cleanly."""
    custom = Settings(api_base="https://mirror.example.com", api_timeout_s=5.0)
    seen: list[httpx.Request] = []

    def handler(req: httpx.Request) -> httpx.Response:
        seen.append(req)
        return httpx.Response(200, json={})

    async with ZippClient(settings=custom, transport=httpx.MockTransport(handler)) as c:
        await c.get_latest()

    assert str(seen[0].url).startswith("https://mirror.example.com/api/v1/news/latest")
