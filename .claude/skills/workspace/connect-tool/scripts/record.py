"""MCP Recorder — drive a webapp manually while we capture its API.

Usage:
    uv run --directory tools/mcp-recorder python record.py <url> [session_name]

The browser opens with a persistent session (login survives between runs).
Use the page normally. When you close the browser, we write:
    sessions/<name>/capture.har          full HAR (all network)
    sessions/<name>/endpoints.json       deduplicated XHR/fetch endpoints
    sessions/<name>/endpoints.md         human-readable summary
"""

from __future__ import annotations

import asyncio
import json
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from playwright.async_api import Request, Response, async_playwright

SCRIPT_DIR = Path(__file__).parent
SESSIONS_DIR = SCRIPT_DIR / "sessions"

RESOURCE_TYPES_KEEP = {"xhr", "fetch"}
RESPONSE_BODY_CAP = 5000  # bytes per unique endpoint sample
HEADERS_STRIP = {
    "accept", "accept-encoding", "accept-language", "cache-control",
    "connection", "dnt", "host", "origin", "pragma", "referer",
    "sec-ch-ua", "sec-ch-ua-mobile", "sec-ch-ua-platform",
    "sec-fetch-dest", "sec-fetch-mode", "sec-fetch-site", "sec-fetch-user",
    "upgrade-insecure-requests", "user-agent", "content-length",
}

UUID_RE = re.compile(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}", re.I)
INT_SEG_RE = re.compile(r"^\d+$")


def normalize_path(path: str) -> str:
    """Collapse dynamic path segments (ids, uuids) to `{id}` for dedup."""
    parts = []
    for seg in path.split("/"):
        if not seg:
            parts.append(seg)
            continue
        if INT_SEG_RE.match(seg) or UUID_RE.match(seg):
            parts.append("{id}")
        else:
            parts.append(seg)
    return "/".join(parts)


def fingerprint(method: str, url: str) -> str:
    p = urlparse(url)
    return f"{method.upper()} {p.scheme}://{p.netloc}{normalize_path(p.path)}"


def clean_headers(headers: dict[str, str]) -> dict[str, str]:
    return {k: v for k, v in headers.items() if k.lower() not in HEADERS_STRIP}


def try_parse_json(text: str) -> Any:
    try:
        return json.loads(text)
    except (json.JSONDecodeError, ValueError):
        return None


class Recorder:
    def __init__(self, target_origin: str):
        self.target_origin = target_origin
        self.endpoints: dict[str, dict[str, Any]] = {}
        self.pending: dict[str, Request] = {}

    def should_capture(self, request: Request) -> bool:
        if request.resource_type not in RESOURCE_TYPES_KEEP:
            return False
        parsed = urlparse(request.url)
        # Same-origin or common API subdomain pattern
        req_host = parsed.netloc
        target_host = urlparse(self.target_origin).netloc
        if req_host == target_host:
            return True
        # Accept subdomains of the root domain (e.g. api.tool.com when target is app.tool.com)
        root = ".".join(target_host.split(".")[-2:])
        return req_host.endswith(root)

    async def on_request(self, request: Request) -> None:
        if not self.should_capture(request):
            return
        self.pending[request.url + str(id(request))] = request

    async def on_response(self, response: Response) -> None:
        request = response.request
        if not self.should_capture(request):
            return
        fp = fingerprint(request.method, request.url)
        entry = self.endpoints.get(fp)
        if entry is None:
            entry = {
                "fingerprint": fp,
                "method": request.method,
                "url_sample": request.url,
                "count": 0,
                "request_headers": clean_headers(request.headers),
                "request_body_sample": None,
                "response_status": response.status,
                "response_headers": clean_headers(response.headers),
                "response_body_sample": None,
                "response_is_json": False,
            }
            self.endpoints[fp] = entry

        entry["count"] += 1

        # Request body sample
        if entry["request_body_sample"] is None and request.post_data:
            body = request.post_data[:RESPONSE_BODY_CAP]
            parsed = try_parse_json(body)
            entry["request_body_sample"] = parsed if parsed is not None else body

        # Response body sample (only grab first one per fingerprint)
        if entry["response_body_sample"] is None:
            try:
                text = await response.text()
            except Exception:
                text = None
            if text:
                sample = text[:RESPONSE_BODY_CAP]
                parsed = try_parse_json(sample)
                if parsed is not None:
                    entry["response_body_sample"] = parsed
                    entry["response_is_json"] = True
                else:
                    entry["response_body_sample"] = sample


def summarize_markdown(endpoints: list[dict[str, Any]]) -> str:
    by_host: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for ep in endpoints:
        host = urlparse(ep["url_sample"]).netloc
        by_host[host].append(ep)

    lines: list[str] = ["# Captured Endpoints", ""]
    lines.append(f"Total unique: **{len(endpoints)}**")
    lines.append("")

    # Detect likely auth headers (appearing in most requests)
    header_counts: dict[str, int] = defaultdict(int)
    for ep in endpoints:
        for k in ep["request_headers"]:
            header_counts[k.lower()] += 1
    likely_auth = [k for k, c in header_counts.items() if c >= max(2, len(endpoints) // 2) and any(s in k for s in ("auth", "token", "cookie", "api-key", "x-"))]
    if likely_auth:
        lines.append(f"**Likely auth headers:** {', '.join(sorted(set(likely_auth)))}")
        lines.append("")

    for host, eps in sorted(by_host.items()):
        lines.append(f"## {host}")
        lines.append("")
        eps_sorted = sorted(eps, key=lambda e: (e["method"], e["fingerprint"]))
        for ep in eps_sorted:
            lines.append(f"### {ep['method']} {urlparse(ep['url_sample']).path}")
            lines.append(f"- Fingerprint: `{ep['fingerprint']}`")
            lines.append(f"- Called: {ep['count']}x")
            lines.append(f"- Status: {ep['response_status']}")
            if ep["request_body_sample"] is not None:
                body = ep["request_body_sample"]
                if isinstance(body, (dict, list)):
                    body_preview = json.dumps(body, indent=2)[:400]
                else:
                    body_preview = str(body)[:400]
                lines.append(f"- Request body sample:\n```\n{body_preview}\n```")
            if ep["response_body_sample"] is not None:
                body = ep["response_body_sample"]
                if isinstance(body, (dict, list)):
                    body_preview = json.dumps(body, indent=2)[:600]
                else:
                    body_preview = str(body)[:600]
                lines.append(f"- Response sample{'  (JSON)' if ep['response_is_json'] else ''}:\n```\n{body_preview}\n```")
            lines.append("")
    return "\n".join(lines)


async def run(url: str, session_name: str) -> None:
    session_dir = SESSIONS_DIR / session_name
    profile_dir = session_dir / "profile"
    profile_dir.mkdir(parents=True, exist_ok=True)

    har_path = session_dir / "capture.har"
    endpoints_json = session_dir / "endpoints.json"
    endpoints_md = session_dir / "endpoints.md"

    recorder = Recorder(target_origin=url)

    print(f"\n  Opening {url}")
    print(f"  Session: {session_name}")
    print(f"  Profile dir: {profile_dir}")
    print(f"\n  >>> Navigate the site and do the flows you want to capture.")
    print(f"  >>> When you're done, just CLOSE the browser window.\n")

    async with async_playwright() as pw:
        context = await pw.chromium.launch_persistent_context(
            user_data_dir=str(profile_dir),
            headless=False,
            record_har_path=str(har_path),
            record_har_mode="full",
            viewport={"width": 1280, "height": 900},
        )
        context.on("request", lambda r: asyncio.create_task(recorder.on_request(r)))
        context.on("response", lambda r: asyncio.create_task(recorder.on_response(r)))

        page = context.pages[0] if context.pages else await context.new_page()
        await page.goto(url, wait_until="domcontentloaded")

        close_event = asyncio.Event()
        context.on("close", lambda _: close_event.set())
        await close_event.wait()

    endpoints_list = list(recorder.endpoints.values())
    endpoints_list.sort(key=lambda e: (urlparse(e["url_sample"]).netloc, e["method"], e["fingerprint"]))

    endpoints_json.write_text(json.dumps(endpoints_list, indent=2, default=str))
    endpoints_md.write_text(summarize_markdown(endpoints_list))

    print(f"\n  ✓ Captured {len(endpoints_list)} unique endpoints")
    print(f"  ✓ HAR:       {har_path}")
    print(f"  ✓ JSON:      {endpoints_json}")
    print(f"  ✓ Summary:   {endpoints_md}\n")


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: record.py <url> [session_name]", file=sys.stderr)
        sys.exit(2)
    url = sys.argv[1]
    session_name = sys.argv[2] if len(sys.argv) > 2 else urlparse(url).netloc.replace(".", "_")
    asyncio.run(run(url, session_name))


if __name__ == "__main__":
    main()
