# Zipp MCP

> Multi-language crypto news for AI assistants — editorial summaries,
> sentiment labels (BULLISH / NEUTRAL / BEARISH), importance scores
> (0–100), and every story credited to its original publisher.

[![MCP Endpoint](https://img.shields.io/badge/MCP-zippfeed.com%2Fmcp%2F-1f6feb)](https://zippfeed.com/mcp/)
[![MCP Registry](https://img.shields.io/badge/MCP%20Registry-com.zippfeed%2Fzipp-success)](https://registry.modelcontextprotocol.io/v0/servers?search=zipp)
[![Transport](https://img.shields.io/badge/transport-Streamable%20HTTP-2ea043)](https://modelcontextprotocol.io/)
[![Auth](https://img.shields.io/badge/auth-public%20%E2%80%93%20no%20key-success)](https://zippfeed.com/mcp/)
[![Languages](https://img.shields.io/badge/languages-8-blueviolet)](#languages)
[![License](https://img.shields.io/badge/license-MIT-lightgrey)](LICENSE)

This repository contains the public documentation and listing manifest
for **Zipp's MCP server**. The server itself is hosted at
`https://zippfeed.com/mcp/` — there is nothing to install or self-host.

- 🌐 Website: [zippfeed.com](https://zippfeed.com)
- 🔌 MCP endpoint: `https://zippfeed.com/mcp/`
- 📡 Transport: Streamable HTTP (MCP spec `2025-06-18`)
- 🔓 Auth: none — public, rate-limited at the Cloudflare edge
- 📰 Coverage: crypto / blockchain / Web3 across 8 languages
- ✍️ Editorial: every item carries sentiment + importance + source attribution

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

### Claude.ai web (Connectors)

Settings → Connectors → **Add custom connector** →
URL: `https://zippfeed.com/mcp/` → no authentication.

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
- [`/developer/openapi.json`](https://zippfeed.com/developer/openapi.json) — REST OpenAPI 3.1 spec

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
