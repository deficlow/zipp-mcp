"""Command-line entry point for the Zipp MCP wrapper.

Exposes ``zipp-mcp`` (the script entry registered in pyproject.toml)
and ``python -m zipp_mcp``. Three transports:

* ``stdio`` (default) — for desktop clients like Claude Desktop, Cline,
  Zed via mcp-remote. No port binding.
* ``streamable-http`` / ``http`` — modern MCP HTTP transport, listens
  on ``MCP_HOST:MCP_PORT`` (defaults 127.0.0.1:8080; aliases ``PORT``
  for Railway/Fly/Render/Cloud Run/Heroku).
* ``sse`` — legacy Server-Sent Events transport, kept for older
  hosted-MCP clients still on that path.
"""
from __future__ import annotations

import argparse
import sys
from typing import NoReturn

from zipp_mcp import __version__
from zipp_mcp.server import mcp

_TRANSPORTS = ("stdio", "streamable-http", "http", "sse")


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="zipp-mcp",
        description=(
            "Zipp MCP server — multi-language crypto news for AI assistants. "
            "Wraps the public REST API at https://zippfeed.com/api/v1/news/*."
        ),
    )
    parser.add_argument(
        "--transport",
        "-t",
        default="stdio",
        choices=_TRANSPORTS,
        help="Transport to serve on (default: stdio).",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"zipp-mcp {__version__}",
    )
    return parser


def main(argv: list[str] | None = None) -> NoReturn:
    """Entry point referenced by ``pyproject.toml`` ``[project.scripts]``.

    Always exits — the FastMCP runner blocks until shutdown.
    """
    args = _build_parser().parse_args(argv)
    transport = "streamable-http" if args.transport == "http" else args.transport
    try:
        mcp.run(transport=transport)
    except KeyboardInterrupt:
        # Clean exit when the user Ctrl-Cs a stdio session — don't
        # spam a stack trace.
        sys.exit(0)
    sys.exit(0)


if __name__ == "__main__":
    main()
