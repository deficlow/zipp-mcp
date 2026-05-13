"""
Minimal example: connect to the Zipp MCP server and call `search`.

Requires:
    pip install mcp

The Zipp MCP server is hosted at https://zippfeed.com/mcp/ and requires
no authentication. Output items carry source attribution in the
`source` field — please credit both Zipp and the original publisher
when surfacing this content.
"""

import asyncio
import json

from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

ZIPP_MCP_URL = "https://zippfeed.com/mcp/"


async def main() -> None:
    async with streamablehttp_client(ZIPP_MCP_URL) as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()

            tools = await session.list_tools()
            print("Available tools:")
            for tool in tools.tools:
                print(f"  - {tool.name}: {tool.description}")

            result = await session.call_tool(
                "search",
                {"query": "Bitcoin ETF", "lang": "en-US", "limit": 3},
            )
            print("\nsearch('Bitcoin ETF') →")
            for block in result.content:
                if block.type == "text":
                    print(json.dumps(json.loads(block.text), indent=2))


if __name__ == "__main__":
    asyncio.run(main())
