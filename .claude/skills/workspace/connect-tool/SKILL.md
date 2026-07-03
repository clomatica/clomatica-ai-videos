---
name: connect-tool
description: Connect a new tool (SaaS app, internal website, any webapp) to Claude so it can read data, trigger actions, or automate work in that tool. Tries official integrations first (pre-built catalog, vendor or community MCP servers, public APIs) and falls back to a Playwright-based browser recorder only for tools without any of those — the user navigates the site while the recorder captures traffic in the background. Use whenever the user says "connect [tool]", "add integration", "integrate [tool]", "automate [tool]", "make Claude work with [X]", "can you use [tool]?", "use [tool name]", or names any product they want Claude to reach — even if the tool is internal, obscure, or has no API documentation. Also trigger on "what can I connect" or "show me available tools".
metadata:
  maintainer: All Teams
  last-updated: 2026-07-03
  department: Workspace
---

# Connect a Tool

Add a new tool connection to this workspace. Always prefer official integrations over custom ones — they're maintained by the vendor (or the community), break less often, and already handle edge cases we'd miss. The Playwright recorder is the **last resort**, not the first stop.

## Priority order

When the user asks to connect a tool, try these in order and stop at the first one that works:

1. **Flow A — Catalog.** Known tool with a ready-made integration in this workspace (Slack, Notion, Linear, Shopify, ManyChat, etc.).
2. **Flow B — Official MCP.** Vendor or community MCP server exists but isn't in our catalog yet. Install it and add it to the catalog for next time.
3. **Flow C — Official API.** No MCP but the tool has public API docs. Build a small MCP server from the docs (WebSearch / WebFetch the docs, generate from `references/server-template.py`).
4. **Flow D — Recorder.** No MCP, no public API, or internal tool. User drives the browser, Playwright captures the network traffic, we reverse-engineer the connection from what we saw.

Never say "MCP" to the user. Say "connection" or the tool's name. The output folder is called `custom-mcps/` internally, but the user never needs to see or type that.

---

## Two Non-Negotiable Rules

**1. Credentials live in `.mcp.json` — nowhere else.**
Not in `.env`, not in environment variables the user sets manually, not hardcoded. The Python server reads from env vars first, then falls back to reading `.mcp.json` directly — and that fallback is what actually works reliably (env injection from Claude Code is flaky). Don't create `.env` entries for a custom tool. Don't tell the user to `export FOO=bar`. `.mcp.json` is the one place.

**2. `.mcp.json` paths break silently — always verify.**
The `--directory` field in a `.mcp.json` entry is a relative path from the workspace root. If it's wrong by a single character (typo, case, accent, wrong folder name), Claude Code will silently fail to start the server and the new connection will just not appear. After writing the entry, always:
- Confirm `custom-mcps/<tool-name>/server.py` exists on disk at that path.
- Print the **absolute path** of both the `.mcp.json` file and the server folder back to the user so they can see them.

If the user reloads and the new tool doesn't appear, the path in `.mcp.json` is the first thing to re-check.

---

## Step 1: What tool?

If the user hasn't said yet, ask in en: "What tool do you want to connect?"

Then walk the priority order. **Don't jump to the recorder just because the tool is unfamiliar** — check for an official integration first. The recorder is expensive: it takes the user's time, captures their session, and produces a reverse-engineered connection we own. An official MCP or API is almost always a better long-term answer.

If the user asks "what's available" or similar, show them the catalog grouped by effort level.

---

## Flow A — Catalog (known tools)

### A.1 — Plug & Play (OAuth plugins, under a minute)

| Tool | What you can do |
|------|-----------------|
| **Slack** | Read channels, post messages, search conversations |
| **Notion** | Search pages, read docs, create content |
| **Linear** | Manage issues, track projects, update statuses |
| **Jira / Atlassian** | Browse projects, manage tickets |
| **Figma** | Access designs, read file contents |

Tell the user: "Type `/plugins` in this chat → arrow-key to the tool → press Enter → choose **Authenticate** → finish OAuth in the browser → reload Claude Code (Cmd+Shift+P → 'Reload Window')."

There is no `claude mcp auth ...` CLI. All plugin auth goes through `/plugins`.

### A.2 — Shopify (official plugin, 2-3 minutes)

Shopify ships its own Claude Code plugin + CLI.

1. Check Shopify CLI is installed: `shopify version` (needs 3.93+). Install with `brew install shopify-cli` on Mac.
2. `/plugin marketplace add Shopify/shopify-ai-toolkit`
3. `/plugin install shopify-plugin@shopify-plugin`
4. Reload Claude Code.
5. Ask the user for their store domain (`<store>.myshopify.com`).
6. Verify by listing recent products; the plugin runs `shopify store auth` on first use.

### A.3 — API-Key Tools (pre-built, 2-3 minutes)

These have ready-made entries in `references/custom-mcp-catalog.json`:

| Tool | What you need |
|------|---------------|
| **ManyChat** | API token (Settings → API) |
| **Klaviyo** | Private API key |
| **Odoo** | Instance URL + DB name + user + API key |
| **ResourceSpace** | Instance URL + username + API key |
| **Fal** | API key |
| **Granola** | API key |

1. Copy the tool's entry from `references/custom-mcp-catalog.json` into both `.mcp.example.json` (with placeholder values) and `.mcp.json` (with empty strings).
2. Ask the user for their credentials, tell them where to find each in the tool's settings.
3. The user pastes real values **into `.mcp.json`** (the empty fields you added) and saves. Never ask them to set env vars or use `.env`.
4. Verify the `--directory` path in the entry actually exists on disk. Print the absolute path.
5. Reload Claude Code.
6. Run a simple read (list, search) to confirm it works.

### A.4 — Native (already work)

| Tool | How |
|------|-----|
| **GitHub / GitLab** | Git CLI is already installed. No config. |
| **PostgreSQL** | Credentials in `.env`, queried via `query-postgres` skill. (This is the *only* case where `.env` is correct.) |

### A.5 — Catalog wrap-up

Confirm it works with a quick demo using the user's real data. Suggest 2-3 concrete things they can now do.

---

## Flow B — Official MCP (vendor or community)

Tool isn't in our catalog. Before doing anything custom, check if a vendor or community already ships an MCP server for it — that's strictly better than anything we can build ourselves.

### B.1 — Look for an official MCP

Search in this order:

1. **Claude Code plugin marketplaces.** Run:
   ```bash
   claude plugin list --available --json
   ```
   Scan the output for an entry matching the tool name.
2. **Official MCP registry / awesome-mcp lists.** `WebSearch` for `"[tool name] MCP server"` and `"[tool name] modelcontextprotocol"`. Prefer results from the vendor's own docs or `github.com/modelcontextprotocol/servers`.
3. **Vendor documentation.** `WebFetch` the tool's docs index and look for an "AI", "MCP", "Claude", or "integrations" section. Many vendors now ship their own.

**Accept** an MCP when it's maintained by the vendor, or a community package with meaningful recent activity (commits in the last ~6 months, not one-person-one-commit). Skip toy projects.

### B.2 — Install and register

If the MCP is a Claude Code plugin: install via `claude plugin install <name>` and tell the user to run `/plugins` → Authenticate (if OAuth) or add credentials.

If it's a standalone npm / Python package: add a `mcpServers` entry in `.mcp.json` and `.mcp.example.json` following the install command the package documents. Credentials still go in the `env` block of `.mcp.json` — never in `.env`, never as raw environment variables. Verify the entry's paths / commands resolve on disk before telling the user anything (same path-verification rule as Flow D.8).

### B.3 — Add to catalog

If it wasn't in `references/custom-mcp-catalog.json`, add it there so the next workspace connects faster. The catalog is the institutional memory of every tool we've ever connected.

### B.4 — Verify and wrap up

Confirm with a simple read operation. If it works, we're done — no recorder needed.

---

## Flow C — Official API (no MCP, but public docs)

No official MCP exists, but the tool has public API documentation. Build a thin MCP from the docs. Still preferable to the recorder because the docs tell us the full API surface, auth model, rate limits, and pagination — things the recorder can only guess at.

### C.1 — Confirm real public docs exist

`WebSearch` for `"[tool] API documentation"` and `"[tool] developer portal"`. Visit the top 1-2 hits with `WebFetch` and check:
- Is there a documented base URL and a list of endpoints?
- Is the auth model explicit (API key, OAuth, HMAC)?
- Is it available to regular customers, or behind an enterprise-only wall?

If any of that is missing or walled off → skip to Flow D (recorder). A half-documented API produces a half-working MCP.

### C.2 — Gather intent (same as recorder path)

Ask what they want to be able to do with it, in plain language. List the operations — each becomes one `@mcp.tool()`.

### C.3 — Research the relevant endpoints

`WebFetch` only the doc pages for the operations you actually need. Note for each endpoint:
- Full URL, method, required parameters.
- Auth header / token shape.
- Response structure (field names that will go into the human-readable output).
- Pagination and rate-limit notes.

### C.4 — Generate, register, hand off

Same code-generation path as Flow D.7-D.9 below — copy `references/server-template.py` and `references/pyproject-template.toml`, fill the env keys, implement the tools, register in `.mcp.json` + `.mcp.example.json`, verify the `--directory` path, tell the user to fill credentials and reload.

Also add the tool to `references/custom-mcp-catalog.json`.

---

## Flow D — Recorder (last resort)

No official MCP, no public API, or the tool is internal. Reverse-engineer by recording the user's real browser session while they perform the operations they want to automate.

### D.1 — Gather intent

Ask two short questions, in en, one at a time:

1. **"What's the URL of [tool]?"** — e.g. `https://retail.rondanet.com`
2. **"What do you want to be able to do with it?"** — in plain words. "List customers", "see yesterday's orders", "send a message to a contact". Each of these becomes a callable operation later, so write them down.

### D.2 — Prepare the recorder (first run only)

The recorder is a Playwright script at `scripts/record.py` inside this skill's folder. It opens a real Chrome window and captures every XHR/fetch call the tool makes.

Before the first custom connection, the recorder's own dependencies have to be installed. This should already have been done by the workspace setup script (Playwright + Chromium), so the check below is usually a no-op. If `scripts/.venv/` doesn't exist, install:

```bash
cd <this-skill-folder>/scripts && uv sync && uv run playwright install chromium
```

Tell the user, in en: "First-time setup — installing the browser I'll use. One minute." Only say that if you actually had to run the install.

### D.3 — Launch and explain

Tell the user, in plain en, without jargon:

- "I'm going to open a Chrome window pointing at [URL]."
- "You'll see a bar up top saying 'Chrome is being controlled by automated test software' — that's normal, it's me."
- "Log in as you always would. The session stays saved locally, so next time you won't have to log in again."
- "Then just do the things you want me to handle later: [read back their list from D.1]."
- "When you're finished, **close the Chrome window**. Closing it is how I know you're done."

Launch the recorder in background. Session name is kebab-cased from the tool's domain (e.g. `retail.rondanet.com` → `rondanet`):

```bash
uv run --directory <this-skill-folder>/scripts python record.py <URL> <session-name>
```

Wait for the background process to exit — it exits automatically when the user closes the browser.

### D.4 — Read the capture

Read the output files under `scripts/sessions/<session-name>/`:

- `endpoints.md` — human-readable summary grouped by host, with request/response samples and a "Likely auth headers" line at the top.
- `endpoints.json` — full structured data for every unique endpoint.

These files may contain the user's password and session tokens if the tool uses form-based login. Treat as sensitive. They live in a gitignored `sessions/` folder.

### D.5 — Analyze

From `endpoints.json`, work out:

- **Auth mechanism.** Find the header that appears in most/all requests: `Authorization: Bearer ...`, `Cookie: ...`, `X-API-Key: ...`, or a custom header. That's the auth.
- **Login flow.** If the capture shows `POST /.../login` (or similar) followed by authenticated calls, the connection needs to reproduce that login in code. Note the login body shape (`usuario`, `email`, `password`, etc.) and where the token sits in the response (`data.token`, `access_token`, etc.).
- **Multi-step auth.** Some tools log in twice — once with email+password, then again to switch to an organization / company / workspace, returning a new token used for all real calls. Look for a second `POST /auth/...` or `POST /switch/...`. If present, the connection must chain both.
- **Account-scoped IDs embedded in URLs.** If an ID (UUID or Mongo ObjectId shape) appears hardcoded in paths, check whether it was returned by the login response (e.g. `businesses[0].id`). If yes → auto-detect, don't make the user enter it. If no → add it to the config as an override.
- **Map operations to endpoints.** For each operation from D.1, find the matching endpoint. Operations named but never performed during the capture → missing. Ask the user to run the recorder again on that specific flow.

### D.6 — Confirm with the user

Show the mapping back, in their language. Example:

> "Here's what I got from your session:
> - 'List customers' → `GET /api/v2/customers` (you hit it 3 times)
> - 'See one customer' → `GET /api/v2/customers/{id}`
> - 'Send a message' → `POST /api/v2/messages`, body needs `{contactId, text}`
>
> Auth: you log in with email + password, the site gives back a token that's used for every call. I'll handle the login automatically — you just need to put your email and password into `.mcp.json` once. Sound right?"

If anything's off, ask them to re-run the recorder on the missing flow. Don't guess.

### D.7 — Generate the connection

Create `custom-mcps/<tool-name>/` — pick a short kebab-cased name from the tool's domain. Copy and fill these templates:

**`pyproject.toml`** from `references/pyproject-template.toml`:
- Fill `{{MCP_SERVER_NAME}}` (e.g. `rondanet`)
- Fill `{{SHORT_DESCRIPTION}}` (one-liner from D.1)
- Add extra deps only if strictly needed

**`server.py`** from `references/server-template.py`:
- Fill `{{SERVICE_NAME}}` and `{{MCP_SERVER_NAME}}` consistently
- Fill `{{ENV_KEYS}}` — the list of credential keys the user will fill in `.mcp.json`
- Keep the `_load_config()` helper as-is. It reads env vars first, then falls back to reading `.mcp.json` directly. The fallback is the path that actually works. **Never replace it with bare `os.environ.get()`.**
- **If auth is a single API key / Bearer token header:** just attach it in an `_client()` helper and go.
- **If auth is login-based:** add a `_login()` helper that posts to the login endpoint, extracts the token, chains the second (org/company) call if multi-step, returns the final bearer. Cache the token in a module-level dict with a TTL (~55 min for 1h server tokens). Wrap requests in `_authed_request()` that retries once with a forced refresh on 401.
- **If the login response has useful data** (list of workspaces, user id, etc.): extract and use it — don't ask the user for values the server already returned.
- For each confirmed operation from D.6, add one `@mcp.tool()` function:
  - Docstring in plain English — this becomes the tool description Claude sees.
  - Typed parameters with sensible defaults (dates, pagination).
  - Return **human-readable text**, not raw JSON. Use the actual field names from the captured response so the output looks useful.
  - Let exceptions bubble; the MCP framework surfaces them to Claude.

Install dependencies:
```bash
cd custom-mcps/<tool-name> && uv sync
```

Smoke-test the server imports before moving on:
```bash
cd custom-mcps/<tool-name> && uv run python -c "from server import mcp; print('ok')"
```

### D.8 — Register the connection (the path-sensitive step)

Two files, both at the workspace root:

**`.mcp.example.json`** (git-tracked, placeholders only):
```json
{
  "mcpServers": {
    "<tool-name>": {
      "command": "uv",
      "args": ["run", "--directory", "custom-mcps/<tool-name>", "server.py"],
      "env": {
        "<TOOL>_USUARIO": "your-email",
        "<TOOL>_CONTRASENA": "your-password"
      }
    }
  }
}
```

**`.mcp.json`** (gitignored, user-filled):
- Same entry, env values set to empty strings.
- The `env` block here is where the credentials will actually live. Never ask the user to set them anywhere else.

**Verify the path.** Right after writing `.mcp.json`, check:

```bash
ls custom-mcps/<tool-name>/server.py
```

If that `ls` fails, the `--directory` value is wrong — fix before telling the user anything. Then print the absolute path so the user can eyeball it:

```bash
echo "Server path: $(pwd)/custom-mcps/<tool-name>/server.py"
echo "Config file: $(pwd)/.mcp.json"
```

This is the most common silent failure — Claude Code won't tell you the path is wrong, the server just doesn't appear. Getting it right here saves a confusing debug session later.

Also add the entry to `references/custom-mcp-catalog.json` so future workspaces can connect the same tool faster.

### D.9 — Hand off to the user

Tell them, in plain en:

1. "The connection is built. Two small things left:"
2. "Open **`.mcp.json`** — I already added the `<tool-name>` section. Paste your real credentials into the empty fields and save."
3. "Reload Claude Code: Cmd+Shift+P → 'Reload Window'."
4. "Then ask me: 'list my [thing] from [tool]'. I'll use the new connection."

**Do not** run a test yourself yet — credential entry is theirs to complete. If they come back saying it's not working, go to Troubleshooting.

---

## Examples

**Catalog (plug & play):**

> User: "Connect Slack"
> Claude: [Flow A.1] "Type `/plugins`, find Slack, Authenticate, reload window. I'll wait."

**Catalog (API-key):**

> User: "Connect our ManyChat"
> Claude: [Flow A.3] Copies the manychat entry to `.mcp.json`, asks for the API token (Settings → API in ManyChat), user pastes into `.mcp.json`, Claude verifies the `--directory` path exists, user reloads.

**Official MCP (not in our catalog):**

> User: "Connect Stripe"
> Claude: [Flow B] Not in catalog. `claude plugin list --available` doesn't show it. `WebSearch "Stripe MCP server"` finds `@stripe/mcp` on npm maintained by Stripe. Install via the standard `mcpServers` pattern, user gets a restricted API key from Stripe's dashboard, pastes it into `.mcp.json`, reload, done. Added to `custom-mcp-catalog.json` for next workspace.

**Official API (no MCP):**

> User: "Connect Splitwise"
> Claude: [Flow C] Not in catalog, no MCP found. Splitwise has a public REST API with OAuth. Fetches the relevant docs, user wanted "list my expenses" + "see who owes what" → Claude generates a small MCP with two tools from `references/server-template.py`, registers, user generates an API key in their Splitwise account.

**Recorder (login-based, multi-step auth, no API):**

> User: "Connect retail.rondanet.com"
> Claude: [Flow D] Not in catalog, no MCP, docs are member-only and not public. Asks what they want to do → user: "list orders, see one in detail" → Claude explains the browser flow, launches recorder, user navigates and closes → Claude reads `endpoints.md`, detects 2-step login (user/password → empresa-token), maps `list_documents` + `get_document`, confirms, builds `custom-mcps/rondanet/` with a `_login()` helper that chains both auth calls, registers in `.mcp.json`, checks the path resolves, tells user to fill credentials and reload.

---

## Troubleshooting

| Problem | Cause | Fix |
|---------|-------|-----|
| Reload + new tool doesn't appear | `.mcp.json` `--directory` path is wrong | Re-check the value character by character. Confirm `custom-mcps/<tool-name>/server.py` exists. Absolute path mismatch is the #1 silent failure. |
| Server spawns but tool calls fail with missing-credentials error | User put credentials in `.env` instead of `.mcp.json`, or didn't save `.mcp.json` | Direct them back to `.mcp.json`. That's the only place credentials belong. |
| Recorder window opens but captures nothing useful | User stayed on a login page or static page; no actual actions performed | Ask them to re-run and actually do the flow they want automated. Landing pages don't fire API calls. |
| Capture has 40+ irrelevant endpoints | Analytics / telemetry / ads / websocket probes | Analysis step filters — skip hosts matching `notifications*`, `tracking*`, `telemetry*`, `/ws/info`, `crearTraficoDeAplicacion`. Focus on hosts that carry real data. |
| Generated connection returns 401 immediately | Login step missing from capture, or token not being sent | Re-check the capture for the actual auth mechanism. Could be cookie-based (cookies expire, user may need to re-paste periodically). |
| Multi-step auth failing silently | First login succeeded, but the second (org/workspace) call didn't run or returned a different token | Log both response bodies. Confirm you're using the second token for all subsequent calls, not the first. |
| `uv` not installed | Workspace setup incomplete | `curl -LsSf https://astral.sh/uv/install.sh \| sh` |
| Chromium not installed | First-run setup skipped or failed | `uv run --directory <this-skill-folder>/scripts playwright install chromium` |

---

## Self-Improvement

After finishing a custom connection (Flow D), check for patterns worth codifying:
- A new auth pattern (e.g. SAML bounce, PKCE, signed requests) → document the pattern in `references/server-template.py` as a comment block.
- A dep that came up and would come up again → add to `references/pyproject-template.toml`.
- A step that was unclear to the user → fix this SKILL.md.
- A new ready-to-use integration → add it to `references/custom-mcp-catalog.json`.

Skills improve by documenting what actually happened. Don't speculate.
