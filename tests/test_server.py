"""Smoke tests for the FastMCP server module.

We don't spin up the whole MCP transport here — that's covered by
the official `mcp` library's own tests. We check:

  * Import side-effects are clean (no network, no env reads beyond
    settings defaults).
  * All 6 tools registered with the expected names.
  * Server identity strings match what the hosted Zipp announces.
"""
from __future__ import annotations

import pytest


def test_module_imports_cleanly() -> None:
    import zipp_mcp.server as srv  # noqa: F401  (import is the assertion)


def test_mcp_instance_metadata() -> None:
    from zipp_mcp.server import mcp

    assert mcp.name == "Zipp"
    assert "BULLISH" in (mcp.instructions or "")
    assert "Importance >= 75" in (mcp.instructions or "")


@pytest.mark.parametrize(
    "tool_name",
    [
        "search",
        "get_latest",
        "get_breaking",
        "get_featured",
        "get_post",
        "list_categories",
    ],
)
async def test_each_tool_registered(tool_name: str) -> None:
    from zipp_mcp.server import mcp

    tools = await mcp.list_tools()
    names = {t.name for t in tools}
    assert tool_name in names, f"tool {tool_name!r} missing from registry; got {names}"


def test_cli_module_imports() -> None:
    """The CLI entry point must import without side effects so package
    install hooks (entry-point resolution) don't crash."""
    import zipp_mcp.cli as cli

    parser = cli._build_parser()
    args = parser.parse_args(["--transport", "stdio"])
    assert args.transport == "stdio"


def test_cli_rejects_unknown_transport() -> None:
    import zipp_mcp.cli as cli

    with pytest.raises(SystemExit):
        cli._build_parser().parse_args(["--transport", "carrier-pigeon"])
