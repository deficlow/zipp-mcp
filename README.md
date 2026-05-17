# Zipp MCP

> Multi-language crypto news for AI assistants — editorial summaries,
> sentiment labels (BULLISH / NEUTRAL / BEARISH), importance scores
> (0–100), and every story credited to its original publisher.

[![MCP Endpoint](https://img.shields.io/badge/MCP-zippfeed.com%2Fmcp%2F-1f6feb)](https://zippfeed.com/mcp/)
[![MCP Registry](https://img.shields.io/badge/MCP%20Registry-com.zippfeed%2Fzipp-success)](https://registry.modelcontextprotocol.io/v0/servers?search=zipp)
[![Smithery](https://smithery.ai/badge/deficlow/zipp)](https://smithery.ai/servers/deficlow/zipp)
[![Transport](https://img.shields.io/badge/transport-Streamable%20HTTP-2ea043)](https://modelcontextprotocol.io/)
[![Auth](https://img.shields.io/badge/auth-public%20%E2%80%93%20no%20key-success)](https://zippfeed.com/mcp/)
[![Languages](https://img.shields.io/badge/languages-8-blueviolet)](#languages)
[![License](https://img.shields.io/badge/license-MIT-lightgrey)](LICENSE)

This repository hosts the **public listing manifest** and the
**`zipp-mcp` Python package**. The canonical Zipp MCP server is
hosted at `https://zippfeed.com/mcp/` — most clients should connect
to that URL directly. The PyPI / Docker package is for the cases
where they can't: stdio-only desktop clients, locked-down networks,
or anywhere you want a self-contained install.

- 🌐 Website: [zippfeed.com](https://zippfeed.com)
- 🔌 MCP endpoint: `https://zippfeed.com/mcp/`
- 📡 Transport: Streamable HTTP (MCP spec `2025-06-18`)
- 🔓 Auth: none — public, rate-limited at the Cloudflare edge
- 📰 Coverage: crypto / blockchain / Web3 across 8 languages
- ✍️ Editorial: every item carries sentiment + importance + source attribution
- 📦 PyPI: `uvx zipp-mcp` · Docker: `ghcr.io/deficlow/zipp-mcp` (Day 3 follow-up)

## Self-host

Three install paths. All three speak the same protocol and call the
same upstream API; the right choice depends on the client.

### `uvx` — no install, one command

For stdio MCP clients (Claude Desktop, Cursor's stdio mode, Cline,
Zed, etc.) that prefer launching a local subprocess:

```bash
uvx zipp-mcp
```

Claude Desktop config (`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "zipp": {
      "command": "uvx",
      "args": ["zipp-mcp"]
    }
  }
}
```

### `pip install` — for embedded use

```bash
pip install zipp-mcp
zipp-mcp --transport stdio
```

Or import the client directly in your own code:

```python
from zipp_mcp import ZippClient

async with ZippClient() as zipp:
    payload = await zipp.search(query="bitcoin etf", lang="en-US", limit=5)
    for item in payload["items"]:
        print(item["title"], item["sentiment"], item["importance"])
```

### Docker — for hosted / sandboxed environments

```bash
docker run -i --rm ghcr.io/deficlow/zipp-mcp
```

For Streamable HTTP transport on a server (Railway, Fly, Render):

```bash
docker run -p 8080:8080 -e MCP_HOST=0.0.0.0 \
  ghcr.io/deficlow/zipp-mcp \
  zipp-mcp --transport http
```

### Configuration

All flags read from env vars too; everything is optional.

| Env var          | Default                | What it does |
|------------------|------------------------|--------------|
| `ZIPP_API_BASE`  | `https://zippfeed.com` | Upstream Zipp deployment (staging, mirror, etc.) |
| `ZIPP_API_TIMEOUT_S` | `30`               | HTTP client timeout (1–120s) |
| `MCP_HOST`       | `127.0.0.1`            | Bind host for HTTP/SSE transports (set `0.0.0.0` in containers) |
| `MCP_PORT`       | `8080`                 | Bind port; also aliased as `PORT` for Railway/Fly/Render/Heroku |

The package is read-only — there is nothing to authenticate; the
upstream API is public and rate-limited at the Cloudflare edge.

## Why Zipp?

Most news connectors are pure aggregators that hand the model a raw
headline list. Zipp adds an **editorial layer** on top of the firehose:

| Signal             | What it does                                                                 |
|--------------------|------------------------------------------------------------------------------|
| **Sentiment**      | Each story labelled `BULLISH` / `NEUTRAL` / `BEARISH` (editorial, not advice) |
| **Importance**     | 0–100 score; `≥ 75` is the *breaking* threshold                              |
| **Multi-language** | 8 languages, native-quality summaries (not auto-translate)                   |
| **Attribution**    | Original publisher name + URL on every item, always                          |
| **Taxonomy**       | 7 categories × 5 sub-leaves = 35 leaves, stable slugs                        |

## Quick start

Zipp speaks **Streamable HTTP** at `https://zippfeed.com/mcp/` — no
auth, no install. Below are copy-paste configs for the major
MCP-capable clients, plus two ways to smoke-test the endpoint.

### Claude Desktop

Add to your `claude_desktop_config.json` (macOS:
`~/Library/Application Support/Claude/claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "zipp": {
      "type": "http",
      "url": "https://zippfeed.com/mcp/"
    }
  }
}
```

Restart Claude Desktop. You should see Zipp in the tool list and be
able to ask things like *"What's breaking in crypto right now?"* or
*"Search Zipp for Bitcoin ETF inflows in Turkish."*

### Claude Code (CLI)

One-liner — registers Zipp at user scope so every project sees it:

```bash
claude mcp add --scope user --transport http zipp https://zippfeed.com/mcp/
```

Verify with `claude mcp list`.

### Claude.ai web (Connectors)

Settings → Connectors → **Add custom connector** →
URL: `https://zippfeed.com/mcp/` → no authentication.

### ChatGPT (Custom Connectors)

Settings → Connectors → **Add** → Custom connector →
URL: `https://zippfeed.com/mcp/` → Authentication: **None**.

### Cursor

`~/.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "zipp": {
      "url": "https://zippfeed.com/mcp/"
    }
  }
}
```

### Windsurf

`~/.codeium/windsurf/mcp_config.json`:

```json
{
  "mcpServers": {
    "zipp": {
      "serverUrl": "https://zippfeed.com/mcp/"
    }
  }
}
```

### Cline (VS Code extension)

Open the Cline panel → **MCP Servers** → **Edit Configuration**, then
add Zipp to `cline_mcp_settings.json`:

```json
{
  "mcpServers": {
    "zipp": {
      "url": "https://zippfeed.com/mcp/",
      "type": "streamableHttp"
    }
  }
}
```

### Zed

`~/.config/zed/settings.json` — Zed's `context_servers` interface is
stdio-only today, so use the [`mcp-remote`](https://www.npmjs.com/package/mcp-remote)
bridge:

```json
{
  "context_servers": {
    "zipp": {
      "command": {
        "path": "npx",
        "args": ["-y", "mcp-remote", "https://zippfeed.com/mcp/"]
      }
    }
  }
}
```

### Gemini CLI

`~/.gemini/settings.json`:

```json
{
  "mcpServers": {
    "zipp": {
      "httpUrl": "https://zippfeed.com/mcp/"
    }
  }
}
```

### OpenAI Responses API

```python
from openai import OpenAI

client = OpenAI()
resp = client.responses.create(
    model="gpt-5",
    tools=[{
        "type": "mcp",
        "server_label": "zipp",
        "server_url": "https://zippfeed.com/mcp/",
        "require_approval": "never",
    }],
    input="What's breaking in crypto right now? Cite the original publisher.",
)
print(resp.output_text)
```

### Anthropic Messages API

The MCP connector is a beta — pass the header below until it goes GA:

```python
import anthropic

client = anthropic.Anthropic()
msg = client.messages.create(
    model="claude-opus-4-7",
    max_tokens=1024,
    mcp_servers=[{
        "type": "url",
        "url": "https://zippfeed.com/mcp/",
        "name": "zipp",
    }],
    messages=[{"role": "user", "content": "What's breaking in crypto right now?"}],
    extra_headers={"anthropic-beta": "mcp-client-2025-04-04"},
)
print(msg.content)
```

### Smoke test

Verify the server from your shell — no client needed:

```bash
curl -s -X POST "https://zippfeed.com/mcp/" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-06-18","capabilities":{},"clientInfo":{"name":"smoke","version":"1.0"}}}'
```

Expected: a JSON-RPC `initialize` result where `serverInfo.name = "Zipp"`
and the server advertises `tools`, `resources`, and `prompts` capabilities.

For an interactive UI, run the official MCP Inspector:

```bash
npx @modelcontextprotocol/inspector
```

In the browser tab that opens, pick **Streamable HTTP** as the
transport, paste `https://zippfeed.com/mcp/`, click **Connect**, then
browse the **Tools / Resources / Prompts** tabs to exercise the
server end-to-end.

## Tools

| Tool              | Signature                                                  | What it returns                                  |
|-------------------|------------------------------------------------------------|--------------------------------------------------|
| `search`          | `(query, lang?, category?, limit?)`                        | Full-text search, recency-first                  |
| `get_latest`      | `(lang?, category?, limit?)`                               | Stories from the last 24 hours                   |
| `get_breaking`    | `(lang?, limit?)`                                          | Importance ≥ 75 within the last 24 hours         |
| `get_featured`    | `(lang?, limit?)`                                          | Editor-curated highlights                        |
| `get_post`        | `(slug_or_id, lang?)`                                      | Full post body + all categories + hashtags       |
| `list_categories` | `(lang?)`                                                  | The 7 × 5 taxonomy (35 leaves)                   |

`lang` defaults to `en-US`. See [Languages](#languages) below for the full list.

### Sample response

`get_latest(lang="en-US", limit=1)` returns shape:

```json
{
  "items": [
    {
      "id": 1234,
      "slug": "bitcoin-etf-inflows-500m",
      "url": "https://zippfeed.com/en-US/a/bitcoin-etf-inflows-500m",
      "title": "Bitcoin ETF inflows hit $500M",
      "summary": "Spot Bitcoin ETFs absorbed $500M in net inflows…",
      "category": "markets-etfs",
      "sentiment": "BULLISH",
      "importance": 82,
      "published_at": "2026-05-13T15:08:55Z",
      "language": "en-US",
      "tags": ["markets-etfs", "btc", "etf"],
      "source": {
        "name": "CoinDesk",
        "url": "https://www.coindesk.com/..."
      },
      "image_url": "https://cdn.zippfeed.com/images/rss/abc.jpg"
    }
  ]
}
```

`get_post` additionally returns the full `body`, `hashtags`, and an
expanded `categories[]` array.

## Languages

| Code     | Language   |
|----------|------------|
| `en-US`  | English    |
| `tr-TR`  | Türkçe     |
| `es-ES`  | Español    |
| `ru-RU`  | Русский    |
| `pt-PT`  | Português  |
| `fr-FR`  | Français   |
| `de-DE`  | Deutsch    |
| `it-IT`  | Italiano   |

Every story is editorially summarised in every supported language;
sentiment and importance scoring are computed once and shared across
language variants.

## Attribution policy

Every Zipp story carries the original publisher in the `source` field.
When you surface Zipp content in an AI response, **please credit both
Zipp and the original publisher**, e.g.:

> *via Zipp — original: CoinDesk*

Linking to the original `source.url` is encouraged. Zipp's own
canonical URL (`item.url`) is the right link when pointing to the
editorial summary.

## Editorial methodology

Zipp's editorial process — feed selection, AI-assisted summarisation,
sentiment + importance scoring, human review — is documented at
[zippfeed.com/en-US/p/methodology](https://zippfeed.com/en-US/p/methodology).

Sentiment is **editorial labelling**, not investment advice.

## Related discovery surfaces

Zipp is published to the official **MCP Server Registry** as
[`com.zippfeed/zipp`](https://registry.modelcontextprotocol.io/v0/servers?search=zipp) —
directories that aggregate the registry (Smithery, Glama, mcp.so,
PulseMCP, etc.) pick it up automatically.

If you're building tooling around Zipp, the following endpoints are
also public:

- [`/llms.txt`](https://zippfeed.com/llms.txt) — AI-discoverable URL map
- [`/sitemap.xml`](https://zippfeed.com/sitemap.xml), [`/news_sitemap.xml`](https://zippfeed.com/news_sitemap.xml), [`/image_sitemap.xml`](https://zippfeed.com/image_sitemap.xml)
- [`/rss.xml`](https://zippfeed.com/rss.xml) + [`/feed.json`](https://zippfeed.com/feed.json) (per-language + per-category + per-slice variants)

The standalone developer REST API was retired on 2026-05-14 — `GET /developer/v1/*` now returns `410 Gone` with a pointer to the MCP endpoint. AI-agent integrations should use MCP; long-form content readers should use the RSS or JSON Feed surfaces above.

## Legal

- [Methodology](https://zippfeed.com/en-US/p/methodology)
- [Privacy](https://zippfeed.com/en-US/p/privacy)
- [Terms](https://zippfeed.com/en-US/p/terms)
- Contact: `hello@zippfeed.com`

## License

This repository — README, manifest, and the example client — is
released under the [MIT License](LICENSE). It covers the **public
documentation and listing manifest only**; the MCP server
implementation itself is proprietary and hosted by Zipp.
