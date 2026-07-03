#!/usr/bin/env python3
"""BrightData MCP Server — fetch recent Instagram/TikTok posts via the Web Scraper API."""

import os
import json
import sys
import time
from datetime import datetime
from typing import Any

import httpx
from mcp.server.fastmcp import FastMCP

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------


def _load_config() -> dict[str, str]:
    """Load config from env vars, falling back to .mcp.json.

    Claude Code is supposed to inject env vars from .mcp.json when spawning
    the MCP server process, but this doesn't always work reliably.
    Try env vars first, then read .mcp.json directly as a fallback.
    """
    env_keys = ["BRIGHTDATA_API_TOKEN"]
    config = {k: os.environ.get(k, "") for k in env_keys}

    if all(config.values()):
        return config

    mcp_json_path = os.path.join(os.path.dirname(__file__), "..", "..", ".mcp.json")
    try:
        # utf-8-sig tolerates a BOM, which Windows editors often add to .mcp.json.
        with open(mcp_json_path, encoding="utf-8-sig") as f:
            mcp_cfg = json.load(f)
        env_block = (
            mcp_cfg.get("mcpServers", {})
            .get("brightdata", {})
            .get("env", {})
        )
        for k in env_keys:
            config[k] = config[k] or env_block.get(k, "")
    except (FileNotFoundError, json.JSONDecodeError):
        pass

    missing = [k for k in env_keys if not config[k]]
    if missing:
        print(
            f"brightdata-mcp: missing config: {', '.join(missing)}. "
            "Set it in .mcp.json (mcpServers.brightdata.env).",
            file=sys.stderr,
        )
        sys.exit(1)

    return config


_config = _load_config()
API_TOKEN = _config["BRIGHTDATA_API_TOKEN"]
API_BASE = "https://api.brightdata.com/datasets/v3"

# Pre-built BrightData scrapers. "discover_new" by profile URL returns the most
# recent posts of each profile (controlled by num_of_posts).
DATASETS = {
    "instagram": {
        "dataset_id": "gd_lk5ns7kz21pck8jpis",
        "discover_by": "url",
        "url_tmpl": "https://www.instagram.com/{handle}/",
    },
    "tiktok": {
        "dataset_id": "gd_lu702nij2f790tmv9h",
        "discover_by": "profile_url",
        "url_tmpl": "https://www.tiktok.com/@{handle}",
    },
}

mcp = FastMCP("brightdata")

# ---------------------------------------------------------------------------
# HTTP helpers
# ---------------------------------------------------------------------------


def _client() -> httpx.Client:
    return httpx.Client(
        timeout=180,
        headers={"Authorization": f"Bearer {API_TOKEN}"},
    )


def _check(r: httpx.Response) -> Any:
    """raise_for_status, but surface BrightData's response body in the error."""
    if r.is_error:
        raise RuntimeError(f"BrightData HTTP {r.status_code} on {r.request.url}\n{r.text}")
    return r.json()


def _normalize(platform: str, raw: str) -> str:
    raw = raw.strip()
    if raw.startswith("http://") or raw.startswith("https://"):
        return raw
    handle = raw.lstrip("@")
    return DATASETS[platform]["url_tmpl"].format(handle=handle)


def _trigger(platform: str, urls: list[str], num: int) -> str:
    ds = DATASETS[platform]
    params = {
        "dataset_id": ds["dataset_id"],
        "include_errors": "true",
        "type": "discover_new",
        "discover_by": ds["discover_by"],
    }
    body = {"input": [{"url": u, "num_of_posts": num} for u in urls]}
    with _client() as c:
        r = c.post(f"{API_BASE}/trigger", params=params, json=body)
        resp = _check(r)
    snapshot_id = resp.get("snapshot_id")
    if not snapshot_id:
        raise RuntimeError(f"trigger did not return a snapshot_id: {resp}")
    return snapshot_id


def _wait_ready(snapshot_id: str, timeout: int = 900, interval: int = 12) -> None:
    deadline = time.time() + timeout
    with _client() as c:
        while time.time() < deadline:
            r = c.get(f"{API_BASE}/progress/{snapshot_id}")
            status = _check(r).get("status", "unknown")
            if status == "ready":
                return
            if status == "failed":
                raise RuntimeError(f"snapshot {snapshot_id} failed")
            time.sleep(interval)
    raise TimeoutError(f"timed out after {timeout}s waiting for snapshot {snapshot_id}")


def _download(snapshot_id: str) -> Any:
    with _client() as c:
        r = c.get(f"{API_BASE}/snapshot/{snapshot_id}", params={"format": "json"})
        return _check(r)


def _results_dir() -> str:
    root = os.path.join(os.path.dirname(__file__), "..", "..")
    d = os.path.join(root, "results", "analyze-profiles")
    os.makedirs(d, exist_ok=True)
    return d


def _first(record: dict, *keys: str, default: str = "") -> Any:
    for k in keys:
        if k in record and record[k] not in (None, ""):
            return record[k]
    return default


def _summarize(records: list, platform: str) -> str:
    lines: list[str] = []
    by_profile: dict[str, list] = {}
    for rec in records:
        if not isinstance(rec, dict):
            continue
        owner = str(_first(rec, "profile_name", "user_posted", "account", "channel", default="?"))
        by_profile.setdefault(owner, []).append(rec)

    for owner, posts in by_profile.items():
        lines.append(f"\n### {owner}  ({len(posts)} posts)")
        for rec in posts:
            date = str(_first(rec, "date_posted", "create_time", "timestamp", default="?"))[:10]
            caption = str(_first(rec, "caption", "description", "post_content", default="")).replace("\n", " ")
            if len(caption) > 160:
                caption = caption[:157] + "..."
            likes = _first(rec, "likes", "num_likes", "digg_count", default="?")
            comments = _first(rec, "num_comments", "comments", "comment_count", default="?")
            views = _first(rec, "views", "play_count", "video_view_count", default="")
            url = _first(rec, "url", "post_url", "video_url", default="")
            eng = f"♥{likes} 💬{comments}" + (f" ▶{views}" if views else "")
            lines.append(f"- [{date}] {eng} — {caption}")
            if url:
                lines.append(f"  {url}")
    return "\n".join(lines) if lines else "(no posts returned)"


# ===================================================================
# TOOLS
# ===================================================================


@mcp.tool()
def fetch_recent_posts(platform: str, profiles: list[str], num_of_posts: int = 5) -> str:
    """Fetch the most recent posts of one or more Instagram or TikTok profiles.

    Use this to research what accounts are posting: topics, tone, formats,
    engagement, and what their characters/personas are like.

    Args:
        platform: "instagram" or "tiktok".
        profiles: handles (with or without @) or full profile URLs.
        num_of_posts: recent posts to pull per profile (default 5).

    Triggers a BrightData collection, waits for it to finish (usually 1-5 min),
    saves the full raw JSON to results/analyze-profiles/, and returns a compact
    per-profile summary plus the saved file path. Read that file for full detail
    (all fields, hashtags, media URLs) before writing an analysis.
    """
    platform = platform.lower().strip()
    if platform not in DATASETS:
        return f"Unsupported platform '{platform}'. Use one of: {', '.join(DATASETS)}."
    if not profiles:
        return "No profiles given."

    urls = [_normalize(platform, p) for p in profiles]
    snapshot_id = _trigger(platform, urls, num_of_posts)
    _wait_ready(snapshot_id)
    records = _download(snapshot_id)

    if not isinstance(records, list):
        records = [records]

    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    out_path = os.path.join(_results_dir(), f"{platform}-{ts}.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)

    header = (
        f"Fetched {len(records)} {platform} posts across {len(urls)} profile(s) "
        f"(snapshot {snapshot_id}).\nRaw JSON saved to: {os.path.abspath(out_path)}\n"
    )
    return header + _summarize(records, platform)


# ===================================================================
# ENTRY POINT
# ===================================================================

if __name__ == "__main__":
    mcp.run()
