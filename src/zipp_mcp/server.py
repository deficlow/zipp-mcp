"""FastMCP server exposing Zipp's news catalogue as 6 MCP tools.

Every tool is a thin shim over :class:`ZippClient` — same arguments,
same response shape as the hosted server at ``https://zippfeed.com/mcp/``.
The wrapper exists so clients that can't (or won't) reach Streamable
HTTP directly still get the editorial layer (sentiment, importance,
source attribution) over a local stdio MCP server.

DNS-rebinding protection is intentionally **off** for the HTTP and
SSE transports. The wrapper is read-only and the upstream API is
public; with the protection on, FastMCP rejects Host headers from
public-facing reverse proxies (Railway, Fly, Render, Cloudflare
Tunnels) with a 421. If you fork this for a write-capable / auth-
gated deployment, flip the flag back on and provide an allowlist.
"""
from __future__ import annotations

from typing import Any

from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings

from zipp_mcp.client import ZippClient
from zipp_mcp.settings import get_settings

# Server metadata surfaces in MCP `initialize` responses and gets
# echoed by clients that show server identity (Claude Desktop tool
# picker, the MCP Inspector). Keep it close to what the hosted Zipp
# advertises so a user moving between transports sees the same name.
_INSTRUCTIONS = (
    "Zipp is a multi-language crypto news aggregator with editorial "
    "summarization, sentiment labelling (BULLISH / NEUTRAL / BEARISH), "
    "and importance scoring (0-100). Languages: en-US, tr-TR, es-ES, "
    "ru-RU, pt-PT, fr-FR, de-DE, it-IT. Every story carries the original "
    "publisher in the 'source' field — when surfacing Zipp content please "
    "credit both Zipp and the original source. Importance >= 75 is the "
    "'breaking' threshold; sentiment is editorial labelling, not financial "
    "advice."
)


def _build_mcp() -> FastMCP:
    settings = get_settings()
    return FastMCP(
        name="Zipp",
        instructions=_INSTRUCTIONS,
        host=settings.mcp_host,
        port=settings.mcp_port,
        transport_security=TransportSecuritySettings(
            enable_dns_rebinding_protection=False,
        ),
    )


mcp = _build_mcp()


_DEFAULT_LANG = "en-US"
_DEFAULT_LIMIT = 10


# ── Tools ───────────────────────────────────────────────────────────────


@mcp.tool(
    name="search",
    description=(
        "Full-text search across Zipp's news catalogue. Returns recent "
        "matching stories ordered by recency (with relevance as a "
        "tiebreaker). Use for questions like 'what's happening with "
        "Bitcoin ETFs?' or 'find news about Solana hacks'."
    ),
)
async def search(
    query: str,
    lang: str = _DEFAULT_LANG,
    category: str | None = None,
    limit: int = _DEFAULT_LIMIT,
) -> dict[str, Any]:
    """Search Zipp news.

    Args:
        query: Search query string (free text, supports ticker synonyms like BTC ↔ Bitcoin).
        lang: BCP-47 language tag. Search is language-locked — TR query → TR results only.
        category: Optional category slug to scope results (see list_categories).
        limit: Max results (1-30, default 10).
    """
    async with ZippClient() as client:
        return await client.search(
            query=query, lang=lang, category=category, limit=limit
        )


@mcp.tool(
    name="get_latest",
    description=(
        "Latest news from the last 24 hours. Optionally scoped to a "
        "category. Returns posts ordered newest-first. Use for 'what's "
        "new today?' or 'what happened in DeFi today?'."
    ),
)
async def get_latest(
    lang: str = _DEFAULT_LANG,
    category: str | None = None,
    limit: int = _DEFAULT_LIMIT,
) -> dict[str, Any]:
    """Get latest news from the last 24h.

    Args:
        lang: BCP-47 language tag (default en-US).
        category: Optional category slug (see list_categories).
        limit: Max results (1-30, default 10).
    """
    async with ZippClient() as client:
        return await client.get_latest(lang=lang, category=category, limit=limit)


@mcp.tool(
    name="get_breaking",
    description=(
        "Breaking news only — last 24 hours, importance score >= 75. "
        "Lower volume than get_latest but every item is market-moving "
        "by Zipp's editorial threshold."
    ),
)
async def get_breaking(
    lang: str = _DEFAULT_LANG,
    limit: int = _DEFAULT_LIMIT,
) -> dict[str, Any]:
    """Get breaking news (importance >= 75) from the last 24h.

    Args:
        lang: BCP-47 language tag (default en-US).
        limit: Max results (1-30, default 10).
    """
    async with ZippClient() as client:
        return await client.get_breaking(lang=lang, limit=limit)


@mcp.tool(
    name="get_featured",
    description=(
        "Editor-picked feature stories (is_featured=TRUE). No time "
        "window. Use when the user wants curated highlights rather "
        "than the firehose."
    ),
)
async def get_featured(
    lang: str = _DEFAULT_LANG,
    limit: int = _DEFAULT_LIMIT,
) -> dict[str, Any]:
    """Get editor-curated featured stories.

    Args:
        lang: BCP-47 language tag (default en-US).
        limit: Max results (1-30, default 10).
    """
    async with ZippClient() as client:
        return await client.get_featured(lang=lang, limit=limit)


@mcp.tool(
    name="get_post",
    description=(
        "Full detail of a single post — title, summary, full body, all "
        "categories, hashtags, source attribution. Accepts either a slug "
        "(from a previous tool call) or a numeric id."
    ),
)
async def get_post(
    slug_or_id: str,
    lang: str = _DEFAULT_LANG,
) -> dict[str, Any]:
    """Get the full content of a single post.

    Args:
        slug_or_id: Either the post slug (e.g. "bitcoin-etf-...") or numeric id.
        lang: BCP-47 language tag (default en-US).
    """
    async with ZippClient() as client:
        return await client.get_post(slug_or_id=slug_or_id, lang=lang)


@mcp.tool(
    name="list_categories",
    description=(
        "List the full Zipp taxonomy (7 main groups × 5 leaves = 35 "
        "categories total). Use to discover valid category slugs for "
        "the search / get_latest tools."
    ),
)
async def list_categories(
    lang: str = _DEFAULT_LANG,
) -> dict[str, Any]:
    """List all active categories in the Zipp taxonomy.

    Args:
        lang: BCP-47 language tag (default en-US).
    """
    async with ZippClient() as client:
        return await client.list_categories(lang=lang)
