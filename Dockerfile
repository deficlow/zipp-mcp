# syntax=docker/dockerfile:1
#
# Zipp MCP — multi-language crypto news MCP server.
#
# Builds the ``zipp-mcp`` Python package and runs it as a stdio MCP
# server by default. The hosted Streamable HTTP endpoint at
# https://zippfeed.com/mcp/ is the canonical entry; use this image
# when you need:
#
#   * a stdio MCP for a client that can't speak Streamable HTTP
#     (older Claude Desktop releases, certain corporate setups)
#   * a self-contained artifact directory checks can score (Glama,
#     awesome-mcp-servers)
#   * a way to run the server against a non-prod Zipp deployment
#     (set ZIPP_API_BASE to point elsewhere)
#
# Run:
#   docker run -i --rm ghcr.io/deficlow/zipp-mcp
#
# Streamable HTTP transport (e.g. for hosting):
#   docker run -p 8080:8080 -e MCP_HOST=0.0.0.0 \
#     ghcr.io/deficlow/zipp-mcp zipp-mcp --transport http

# ─── Build stage ─────────────────────────────────────────────────────────
FROM python:3.13-slim-bookworm AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /build

# Copy only what's needed for the wheel — keeps build cache layers
# clean when source changes but pyproject.toml does not.
COPY pyproject.toml README.md LICENSE ./
COPY src/ ./src/

RUN pip install --no-cache-dir build hatchling \
 && python -m build --wheel --outdir /wheels


# ─── Runtime stage ───────────────────────────────────────────────────────
FROM python:3.13-slim-bookworm

LABEL io.modelcontextprotocol.server.name="com.zippfeed/zipp" \
      org.opencontainers.image.title="zipp-mcp" \
      org.opencontainers.image.description="Multi-language crypto news MCP server — sentiment + importance + source attribution across 8 languages." \
      org.opencontainers.image.source="https://github.com/deficlow/zipp-mcp" \
      org.opencontainers.image.url="https://zippfeed.com" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.vendor="Zipp"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    ZIPP_API_BASE=https://zippfeed.com \
    MCP_HOST=127.0.0.1 \
    MCP_PORT=8080

COPY --from=builder /wheels/*.whl /tmp/
RUN pip install --no-cache-dir /tmp/*.whl && rm /tmp/*.whl

# Non-root, deterministic uid.
RUN groupadd --system --gid 10001 app \
 && useradd  --system --uid 10001 --gid app app
USER app

EXPOSE 8080

# stdio by default so a plain `docker run -i ... zipp-mcp` slot into a
# stdio MCP client out of the box. Override for hosted deployments,
# e.g. `... zipp-mcp --transport http`.
CMD ["zipp-mcp", "--transport", "stdio"]
