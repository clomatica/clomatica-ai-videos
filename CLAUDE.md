# Clomatica — AI Workspace

This is your company's AI workspace. It grows smarter through use — every process you do together with Claude can be saved as a reusable skill.

---

## Critical Rules

- Never read, display, or modify `.env` or `.mcp.json` — they contain secrets. You may only `source .env` to load variables.
- Never add secrets to git-tracked files. Store in `.env` (skills) or `.mcp.json` (MCP servers) — both gitignored.
- All skill output goes to `results/`.
- Use `AskUserQuestion` with multiple-choice options for all questions. One question at a time.
- All learnings must go to git-tracked files (skills, context, CLAUDE.md) — never to personal `MEMORY.md`.

---

## How to Work

- If this workspace hasn't been configured yet (the profile is empty or there are no company skills), suggest running `/setup` first.
- Before starting any task, check if a skill exists (see Skills by Department below). Use it instead of manual work.
- Always look in `.claude/context/` first before searching elsewhere — `context/company/profile.md` holds what the setup wizard collected about the company. Context files are the source of truth.
- At the end of a repeatable process, offer to save it as a skill (`/create-skill`).

---

## Skills by Department

### Workspace

The base skills that manage the workspace itself:

| Skill | Description |
|-------|-------------|
| `/setup` | Configure this workspace — connect tools, show what I can do, do real work together, personalize everything. Run this first. |
| `/connect-tool` | Connect a new tool (Slack, Notion, your CRM — anything) so Claude can work with it |
| `/save-changes` | Save your work so nothing is lost — sets up the online backup automatically the first time |
| `/audit-workspace` | Health check — find what can be improved in this workspace |
| `/contact-olympus` | Talk to your Olympus AI team — send a health report, a question, an idea, or a bug report |
| `/ai-tips` | Practical tips for getting the most out of working with Claude |

### Shared

Cross-team utilities:

| Skill | Description |
|-------|-------------|
| `/create-skill` | Turn a repeatable process into a reusable skill, or improve an existing one |

### Content

Research and ideation for the videos:

| Skill | Description |
|-------|-------------|
| `/analyze-profiles` | Pull the last posts of Instagram/TikTok profiles (via BrightData) and analyze topic trends, tone, formats and what the characters are like — feeding ideation for Coco & Luna videos |

More departments appear here as `/setup` personalizes the workspace and skills get created from your real work.

---

## Directory Structure

```
.claude/
├── skills/                 # Your skills, grouped in folders by department
│   └── workspace/          # The base skills that manage the workspace itself
│       └── contact-olympus/references/olympus-workspace.json  # Workspace identity — used by /contact-olympus and the daily signal
├── context/company/        # Company profile and context
├── context/videos/         # Estilo de los videos y personajes (Coco & Luna)
├── context/business-model/ # Cómo monetiza el contenido
│   ├── coco-luna/          # Monetización del estilo Coco & Luna (plataformas + modelos)
│   └── youtube-monetizacion/ # Estrategia YouTube long-form (RPM por vertical)
├── logs/                   # Learning and observation logs
├── hooks/phone-home.py     # Once-a-day "workspace is alive" signal to your Olympus team
├── settings.json           # Runs the daily signal when a session starts
results/                    # Skill output files
```

---

## Olympus Connection (do not remove)

This workspace stays connected to the Olympus AI team that supports it, through three files:

- `.claude/skills/workspace/contact-olympus/references/olympus-workspace.json` — this workspace's identity: a session code plus the addresses that `/contact-olympus` sends to.
- `.claude/hooks/phone-home.py` — sends a small once-per-day "workspace is alive" signal to the Olympus team when a session starts. It sends ONLY the date, the total number of skills, and the date of the last save — never file contents, business data, or anything proprietary. It runs silently, never blocks or slows a session, and does nothing when offline.
- `.claude/settings.json` — the setting that runs that signal at session start.

Never delete, move, or edit these files (including during `/audit-workspace` cleanups) — without them the Olympus team can't see that the workspace is healthy, and `/contact-olympus` loses its identity. If the user asks what these files are, explain the above in plain language.

