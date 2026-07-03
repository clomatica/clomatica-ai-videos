#!/usr/bin/env python3
"""{{SERVICE_NAME}} MCP Server — {{SHORT_DESCRIPTION}}."""

import os
import json
import sys
from typing import Any, Optional

import httpx
from mcp.server.fastmcp import FastMCP

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------


def _load_config() -> dict[str, str]:
    """Load config from env vars, falling back to .mcp.json.

    Claude Code is supposed to inject env vars from .mcp.json when spawning
    the MCP server process, but this doesn't always work reliably.
    This function tries env vars first, then reads .mcp.json directly as a
    fallback to guarantee the server can always find its credentials.
    """
    # 1. Try environment variables (set by Claude Code from .mcp.json env block)
    env_keys = {{ENV_KEYS}}  # e.g. ["SERVICE_URL", "SERVICE_API_KEY"]
    config = {k: os.environ.get(k, "") for k in env_keys}

    if all(config.values()):
        return config

    # 2. Fall back to .mcp.json
    mcp_json_path = os.path.join(os.path.dirname(__file__), "..", "..", ".mcp.json")
    try:
        with open(mcp_json_path) as f:
            mcp_cfg = json.load(f)
        env_block = (
            mcp_cfg.get("mcpServers", {})
            .get("{{MCP_SERVER_NAME}}", {})
            .get("env", {})
        )
        for k in env_keys:
            config[k] = config[k] or env_block.get(k, "")
    except (FileNotFoundError, json.JSONDecodeError):
        pass

    # 3. Validate
    missing = [k for k in env_keys if not config[k]]
    if missing:
        print(
            f"{{MCP_SERVER_NAME}}-mcp: missing config: {', '.join(missing)}. "
            "Set them as env vars or in .mcp.json.",
            file=sys.stderr,
        )
        sys.exit(1)

    return config


_config = _load_config()

# Extract config values — customize these for your service
# SERVICE_URL = _config["SERVICE_URL"].rstrip("/")
# SERVICE_API_KEY = _config["SERVICE_API_KEY"]

mcp = FastMCP("{{MCP_SERVER_NAME}}")

# ---------------------------------------------------------------------------
# HTTP helpers
# ---------------------------------------------------------------------------


def _client() -> httpx.Client:
    return httpx.Client(
        timeout=30,
        headers={"Authorization": f"Bearer {_config.get('SERVICE_API_KEY', '')}"},
    )


def _get(endpoint: str, **params: Any) -> dict:
    p = {k: v for k, v in params.items() if v is not None}
    with _client() as c:
        r = c.get(f"{_config['SERVICE_URL']}/api/{endpoint}", params=p)
        r.raise_for_status()
        return r.json()


def _post(endpoint: str, payload: dict) -> dict:
    with _client() as c:
        r = c.post(f"{_config['SERVICE_URL']}/api/{endpoint}", json=payload)
        r.raise_for_status()
        return r.json()


def _fmt(data: Any) -> str:
    if data is None:
        return "No data returned."
    return json.dumps(data, indent=2, ensure_ascii=False, default=str)


# ===================================================================
# TOOLS — Add your @mcp.tool() functions below
# ===================================================================


@mcp.tool()
def example_tool() -> str:
    """Example tool — replace with real tools."""
    return "Hello from {{MCP_SERVER_NAME}}!"


# ===================================================================
# ENTRY POINT
# ===================================================================

if __name__ == "__main__":
    mcp.run()
