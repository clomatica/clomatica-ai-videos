---
name: analyze-profiles
description: Analyze the most recent posts of social media profiles (Instagram and TikTok) to detect topic/situation trends and characterize how the accounts and their characters behave. Use whenever the user gives one or more profiles/handles and wants to know what's trending, what topics they cover, their tone, formats, hooks, hashtags, or "what are these characters like". Pulls the last N posts of each profile through BrightData's Web Scraper API, then writes a trend + character report to results/. Trigger on "analyze these profiles", "look at the last posts of X", "what are these accounts posting", "trend research", "analizá estos perfiles", "mirá los últimos posts de".
metadata:
  maintainer: Content
  last-updated: 2026-07-03
  department: Content
---

# Analyze Profiles — Trend & Character Research

Given one or more social profiles, pull each one's most recent posts and turn them
into a **trend + character report**: what topics/situations they post about, tone,
formats, hooks, captions, hashtags, and what the accounts/characters are *like*.

Built for Clomatica: the point is to feed ideation for cozy animal-couple videos
(see `.claude/context/videos/estilo-videos.md`). Read that file first so the report
speaks to what's actually useful — relatable everyday situations, soft tone, ASMR,
short one-line captions.

Data comes from **BrightData's Web Scraper API** through the `brightdata`
connection (a custom MCP in `custom-mcps/brightdata/`). It exposes one tool:
`fetch_recent_posts` for Instagram + TikTok.

---

## Prerequisites (one time)

The `brightdata` connection needs an API token in `.mcp.json` (gitignored). The
block is already prepared in `.mcp.example.json` — the user copies it into
`.mcp.json` and pastes the real token:

```json
"brightdata": {
  "command": "uv",
  "args": ["run", "--directory", "custom-mcps/brightdata", "server.py"],
  "env": { "BRIGHTDATA_API_TOKEN": "..." }
}
```

Find the token in BrightData: **Account settings → API tokens**. After editing
`.mcp.json`, the user must **reload Claude Code** (Cmd/Ctrl+Shift+P → "Reload
Window") for the connection to appear. If the `brightdata` tool isn't available
yet, tell them to do this and stop. Never print or commit the token — and never
read or modify `.mcp.json` yourself (it holds secrets).

---

## Step 1 — Get the profiles

If the user hasn't already listed them, ask (in es) which profiles to analyze and
on which platform. Accept any of: bare handle (`zachking`), `@handle`, or a full
profile URL. Instagram and TikTok are supported.

If profiles span both platforms, call the tool once per platform.

## Step 2 — Fetch the posts

Call the connection's `fetch_recent_posts` tool, one call per platform. Default is
the last **5** posts per profile (override with `num_of_posts`):

- `platform`: `"instagram"` or `"tiktok"`
- `profiles`: list of handles or profile URLs, e.g. `["profile_a", "@profile_b", "https://www.tiktok.com/@profile_c"]`
- `num_of_posts`: posts per profile (default 5)

The tool triggers the collection, waits for BrightData to finish (usually 1–5 min),
saves the raw JSON to `results/analyze-profiles/<platform>-<timestamp>.json`, and
returns a compact per-profile summary plus that file path. **Read the saved file**
for full detail before analyzing.

If it fails:
- **`brightdata` tool not found** → `.mcp.json` not filled or Claude Code not reloaded (Prerequisites).
- **missing config / HTTP 401/403** → token missing, wrong, or expired.
- **HTTP 400** → a profile URL is malformed, or the account is private/nonexistent.
- **timeout** → re-run; BrightData occasionally queues longer. Snapshots are kept
  30 days, so nothing is lost.

## Step 3 — Read and analyze

Read the saved JSON. Useful fields (names vary a little per platform): `caption` /
`description`, `hashtags`, `likes` / `num_comments` / `views` / `play_count`,
`date_posted`, `url`, `content_type` (post/reel/video), and profile metadata
(`followers`, `profile_name`, `biography`).

For each profile, work out:
- **Topics / situations** — what recurring themes show up across the 5 posts.
- **Tone & humor** — warm, ironic, dramatic, motivational? (Clomatica wants warm,
  relatable, never sarcastic — flag anything reusable.)
- **Format** — reel/carousel/video length, hook style, on-screen text, caption
  length, emoji use.
- **Character** — if the account has recurring characters/personas, describe who
  they are and how they behave (their "personality"). This is the "cómo son los
  personajes" part of the request.
- **What performs** — which of the 5 got the most engagement, and the plausible why.
- **Hashtags** — the recurring ones.

Then synthesize **across all profiles**: shared trends, patterns worth borrowing,
and 3–5 concrete video ideas that fit Clomatica's Coco & Luna style.

## Step 4 — Write the report

Save a markdown report to `results/analyze-profiles/reporte-<YYYYMMDD>.md`, in
**es** (company language). Structure:

1. **Resumen** — the 3–4 biggest takeaways up top.
2. **Por perfil** — one section each: temas, tono, formato, personajes, qué funcionó, hashtags.
3. **Tendencias transversales** — patterns across profiles.
4. **Ideas para Coco & Luna** — 3–5 concrete situations in the estilo-videos format
   (situación de 1 línea + caption). Tie each back to a trend you observed.

Link the raw JSON files at the bottom so the source is traceable.

Keep it skimmable — the user is a solo operator ideating videos, not reading a study.

---

## Notes

- **Dataset IDs** (in `custom-mcps/brightdata/server.py`): Instagram posts
  `gd_lk5ns7kz21pck8jpis`, TikTok posts `gd_lu702nij2f790tmv9h`. If BrightData
  rotates these, update the `DATASETS` dict there.
- To analyze more/less than 5 posts, pass `num_of_posts`.
- Raw JSON and reports live in `results/` (gitignored) — never commit scraped data.
- BrightData bills per record. Each profile × N posts = N records; keep
  `num_of_posts` modest unless the user asks for a deeper pull.
