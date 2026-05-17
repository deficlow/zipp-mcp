"""Zipp MCP — multi-language crypto news server for AI assistants.

Public PyPI package wrapping Zipp's read-only news REST API
(`https://zippfeed.com/api/v1/news/*`) behind the Model Context Protocol.
Use this when your client can't reach the hosted Streamable HTTP
endpoint at `https://zippfeed.com/mcp/` directly — e.g. corporate
networks that block arbitrary outbound HTTPS, agents that only speak
stdio, or anywhere you want a self-contained install via ``uvx
zipp-mcp``.

Tools (mirror the hosted server 1:1):

* ``search`` — full-text search, recency-first
* ``get_latest`` — last 24h
* ``get_breaking`` — importance ≥ 75 from the last 24h
* ``get_featured`` — editor-curated highlights
* ``get_post`` — full detail by slug or numeric id
* ``list_categories`` — the 7 × 5 taxonomy

Source attribution is preserved on every response item — please credit
both Zipp and the original publisher when surfacing this content.
"""
from __future__ import annotations

__version__ = "0.1.0"

from zipp_mcp.client import ZippClient
from zipp_mcp.server import mcp

__all__ = ["__version__", "ZippClient", "mcp"]
