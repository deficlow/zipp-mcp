"""Runtime configuration for the Zipp MCP wrapper.

Loaded once at process start. All fields have safe defaults so
``uvx zipp-mcp`` works with zero env config; override via env vars
when self-hosting on a custom Zipp deployment or behind a proxy.

The host/port aliases (``MCP_PORT`` <-> ``PORT``, ``MCP_HOST`` <->
``HOST``) match the conventions used by Railway, Fly, Render, Cloud
Run, and Heroku so the same image works on all of them without a
per-platform launch script.
"""
from __future__ import annotations

from pydantic import AliasChoices, Field, HttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Wrapper configuration.

    Everything is optional — the defaults point at the public Zipp
    production endpoint with conservative timeouts.
    """

    model_config = SettingsConfigDict(
        env_prefix="ZIPP_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    api_base: HttpUrl = Field(
        default="https://zippfeed.com",  # type: ignore[arg-type]
        description=(
            "Base URL of the Zipp deployment. The wrapper appends "
            "``/api/v1/news/...`` paths to this. Override to point at a "
            "staging environment or a regional mirror."
        ),
    )

    api_timeout_s: float = Field(
        default=30.0,
        ge=1.0,
        le=120.0,
        description="HTTP client timeout (seconds) for upstream calls.",
    )

    mcp_host: str = Field(
        default="127.0.0.1",
        validation_alias=AliasChoices("MCP_HOST", "HOST", "ZIPP_MCP_HOST"),
        description=(
            "Bind host for HTTP / SSE transports. Defaults to loopback so "
            "stdio-only deployments don't accidentally listen on a public "
            "interface; set to 0.0.0.0 for container deployments."
        ),
    )

    mcp_port: int = Field(
        default=8080,
        ge=1,
        le=65535,
        validation_alias=AliasChoices("MCP_PORT", "PORT", "ZIPP_MCP_PORT"),
        description=(
            "Bind port for HTTP / SSE transports. Aliased to ``PORT`` so "
            "Railway, Fly, Render, Cloud Run, and Heroku 'just work'."
        ),
    )


_settings: Settings | None = None


def get_settings() -> Settings:
    """Return the process-wide Settings instance, loading it on first call.

    Tests can monkeypatch this with their own Settings without polluting
    the env.
    """
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


def reset_settings() -> None:
    """Drop the cached Settings — test-only helper."""
    global _settings
    _settings = None
