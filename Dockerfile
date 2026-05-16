# syntax=docker/dockerfile:1
#
# Zipp MCP — stdio bridge for the public Streamable HTTP server at
# https://zippfeed.com/mcp/. Use this image when the client is
# stdio-only (some older Claude Desktop releases, locked-down corporate
# environments); modern clients should connect to the URL directly.
#
# Built on top of the community-maintained mcp-remote proxy:
#   https://github.com/geelen/mcp-remote
#
# Run:
#   docker run -i --rm ghcr.io/deficlow/zipp-mcp
#
# Override the upstream URL (e.g., a staging endpoint):
#   docker run -i --rm -e ZIPP_MCP_URL=https://staging.example.com/mcp/ \
#     ghcr.io/deficlow/zipp-mcp

FROM node:22-alpine

# io.modelcontextprotocol.server.name pins the server identity for MCP
# Registry ownership verification when this image is referenced as an
# `oci` package entry in server.json.
LABEL io.modelcontextprotocol.server.name="com.zippfeed/zipp" \
      org.opencontainers.image.source="https://github.com/deficlow/zipp-mcp" \
      org.opencontainers.image.description="stdio bridge to the public Zipp MCP server (Streamable HTTP)" \
      org.opencontainers.image.licenses="MIT"

# Non-root, deterministic uid (matches the convention used by other
# stdio-bridge images so volume permissions are predictable).
RUN addgroup -S -g 10001 app && adduser -S -G app -u 10001 app
USER app
WORKDIR /home/app

# Pin mcp-remote for reproducible builds. Bump deliberately when a new
# release lands — no package.json on purpose to keep the image minimal.
ARG MCP_REMOTE_VERSION=0.1.38
RUN npm install --no-fund --no-audit --no-progress \
        "mcp-remote@${MCP_REMOTE_VERSION}"

ENV ZIPP_MCP_URL=https://zippfeed.com/mcp/

# stdin must stay open — that's where the JSON-RPC client speaks.
# `sh -c` so the env var is expanded at runtime rather than build.
CMD ["sh", "-c", "exec node node_modules/.bin/mcp-remote \"$ZIPP_MCP_URL\""]
