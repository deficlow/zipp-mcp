"""Test fixtures.

Strategy: every test uses an httpx ``MockTransport`` to stub the
upstream REST API instead of `respx` — fewer deps, identical
ergonomics, and the recorded requests are easier to assert on.
"""
from __future__ import annotations

from collections.abc import Callable
from typing import Any

import httpx
import pytest

from zipp_mcp.client import ZippClient
from zipp_mcp.settings import Settings


@pytest.fixture
def test_settings() -> Settings:
    """A Settings instance pinned to a synthetic base URL.

    The base must be parseable as an HttpUrl but doesn't need to be
    routable — the MockTransport intercepts before any network I/O.
    """
    return Settings(api_base="https://test.invalid", api_timeout_s=5.0)


@pytest.fixture
def record_requests() -> list[httpx.Request]:
    return []


@pytest.fixture
def mock_handler(record_requests: list[httpx.Request]) -> Callable[..., httpx.Response]:
    """Default mock handler — records every request and returns 200 with an empty dict.

    Override per-test by composing your own handler that returns the
    payload you want and asserts on request shape.
    """

    def handler(request: httpx.Request) -> httpx.Response:
        record_requests.append(request)
        return httpx.Response(200, json={})

    return handler


@pytest.fixture
def mock_transport(mock_handler: Callable[..., httpx.Response]) -> httpx.MockTransport:
    return httpx.MockTransport(mock_handler)


@pytest.fixture
async def client(
    test_settings: Settings,
    mock_transport: httpx.MockTransport,
) -> ZippClient:
    """A ZippClient wired to the MockTransport.

    The pytest-asyncio teardown closes the underlying httpx client
    via the test's own ``async with`` or explicit ``aclose``.
    """
    return ZippClient(settings=test_settings, transport=mock_transport)


def make_transport(payload: dict[str, Any], status: int = 200) -> httpx.MockTransport:
    """Helper for tests that want a single fixed response."""

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(status, json=payload)

    return httpx.MockTransport(handler)
