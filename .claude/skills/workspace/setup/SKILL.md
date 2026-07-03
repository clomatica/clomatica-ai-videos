---
name: setup
description: Configure this workspace for a specific company. Greets, reads the wizard data, fetches their links, shows what it learned, offers to connect tools, then dives into real work. Use when the workspace title says "Not Configured Yet", when the user says "follow the setup guide", "set up my workspace", "configure", or on first open.
---

# Workspace Setup

Get the user working in under 5 minutes. The wizard already collected company name, language, links, and selected tools — DO NOT re-ask any of that. The whole flow is four short steps:

1. **Greet** — short hello, tell them what's about to happen
2. **Show what you already know** — read profile.md, fetch their links, summarize
3. **Connect tools** (skippable) — quick pass through installed plugins
4. **Work together** — pick something real and do it

Skip the consultancy-style interview. No questions about culture, values, communication style, who-else-uses-this, pain points. Those will surface naturally during real work and get captured then.

## Principles

- Use `AskUserQuestion` for EVERY question. Multiple-choice when possible.
- One question at a time. Never overwhelm.
- **Never re-ask what's in `profile.md`.** Company name, language, links, tools — already there.
- **Show value before asking for effort.** The wow comes from showing what you read about them, not from interrogating them.
- Keep it conversational. The user may not be technical.
- If something isn't there, skip it — don't dig.

## Resume across sessions

If `results/setup-progress.md` exists, read it and resume from the first unchecked item. Otherwise create it at the start with this slim checklist (create the `results/` directory if needed — NEVER write this file to the workspace root):

```markdown
# Setup Progress

- [ ] Greeted user and got go-ahead
- [ ] Read profile.md
- [ ] Fetched links and shared what was learned
- [ ] Offered to connect installed tools (each one: ✓ connected / — skipped / ⏳ pending)
- [ ] Offered to set up custom integrations (if any)
- [ ] Asked: real task now or consulting interview first? _{pending — must use AskUserQuestion, never default to task}_
- [ ] Did first real task together (or ran `/consulting` if they chose that)
- [ ] Offered to capture task as a skill (if repeatable)
- [ ] Logged setup to learning-log
```

Update the checklist immediately after each step. When all items are checked, delete the file.

---

## Step 1: Greet

**Before reading any files**, greet the user. They just opened a new workspace and don't know what's happening.

1. Run `whoami` to guess a first name (`jsmith` → "J", `john.doe` → "John"). If ambiguous, just "Hello!".
2. Greet them (in their language if you can infer it from `profile.md` filename or session — otherwise English):

> "Hi {name}! Welcome to your AI workspace. Quick rundown of what's about to happen:
>
> 1. I'll read what you already gave me and tell you what I learned
> 2. I'll offer to connect the tools you picked — you can skip any of them
> 3. We'll do something real together
>
> Should take about 5 minutes. Sound good?"

3. Wait for confirmation. Then proceed.

---

## Step 2: Read profile and show what you learned

Read `.claude/context/company/profile.md`. Extract:
- Company name, language, description
- Links under "Company Basics" (Website, LinkedIn, Twitter, Other)
- Tools listed under "Installed Plugins (need authentication)"
- Custom integrations under "Custom Integrations (need API keys)"

Then **`WebFetch` all the links in parallel** — don't ask permission, just do it. From the fetches extract: what the company does, values, product, brand voice, team, key people.

Present what you learned conversationally:

> "Okay, I read your website {and LinkedIn/Twitter if applicable}. Here's what I picked up about {company}:
>
> - [2-3 bullets — what they do, who they serve, brand voice or values, anything specific]
>
> I'll use this to tailor everything. If anything's off, just tell me."

If there were no links in profile.md, skip the fetch and just say:
> "I have your company name and the tools you picked. We'll learn the rest as we work."

**Save the extracted data** for later use — feed it into the workspace files in the background after Step 4.

---

## Step 3: Offer to connect tools

For each tool under "Installed Plugins (need authentication)" in profile.md, ask one at a time:

> "Want to connect **{tool}** now, or skip for later?"
> - Connect now
> - Skip for now

**If "Connect now":** Same flow for every tool — there is no `claude mcp auth ...` CLI command. They do not need to open a terminal.
1. "Right here in **this chat**, type `/plugins` and press Enter — a picker will pop up."
2. "Use the **up/down arrows** to highlight **{tool}** (slug listed in profile.md), press **Enter**."
3. "Choose **Authenticate** and press Enter. Your browser opens — log in and click Allow. Come back when done."
4. "Reload Claude Code: Cmd/Ctrl+Shift+P → 'Reload Window'. Tell me when you're back."
5. Verify by calling a tool from that plugin (Notion → `notion-search`; Gmail → list emails; Google Calendar → list events; Google Drive → list files; Slack → list channels; Linear → list teams). If it fails twice, mark as "auth-pending" and move on. **Never stall.**

Note: Google Workspace is **three separate plugins** — Gmail, Google Drive, Google Calendar. Authenticate each one the client picked.

**If "Skip for now":** Note it. They can connect later by typing `/plugins` themselves.

For each item under "Custom Integrations (need API keys)", ask:

> "**{integration}** needs API keys. Add them now or skip?"
> - Add credentials now
> - Skip for now

If "Add now": tell them which keys are needed (from profile.md) and to put them in `.mcp.json`, then reload. If "Skip": just note it.

---

## Step 4: Choose the next move

Generate the workspace files **silently in the background** starting now (see Step 4b). Don't make the user wait for it.

**This step is a fork — never skip the question.** Do NOT jump straight into asking for a task. Always present the two options first via `AskUserQuestion`. The user's choice determines the rest of setup.

Ask the user:

> "Two options for what we do next:
>
> - **Do something together** — tell me what you've got on your plate and we do it
> - **Tell me more about your company first** — I ask about your team, culture, how work flows, pain points, and tailor everything better
>
> You can do the second one anytime later with `/consulting`, so if you're torn, start by working."

Use `AskUserQuestion`:
- Do something together
- Tell me more about my company first (`/consulting`)

**Wait for their answer. Do not assume.**

**If "Tell me more about my company first":** hand off to `/consulting` — tell them "Great, let's do that" and invoke the consulting skill. After it finishes, ask if they want to do a real task now or wrap up setup.

**If "Do something together":** proceed below.

> "Alright, what do you want to get done right now? Could be anything — an email, a doc, research, a report, processing something. Pick a real task you've got on your plate."

**Wait for them to pick.** Don't suggest unless they explicitly ask. Their pick reveals more about priorities than any interview question.

**Then do the task with them.** Use their connected tools. While working, pay attention to:
- Tools they mention that aren't connected → offer to connect now and continue
- Repeatable steps → potential captured skill
- Their terminology → note for later

After the task is done, if it had repeatable steps:

> "We just {summary}. Want me to save this as a shortcut so anyone on your team can run it next time?"

If yes: create a captured skill at `.claude/skills/{skill-name}/SKILL.md` (flat, one level only). Tell them: "Done — next time just type `/{skill-name}`."

If no, or one-off: just celebrate and explain how it works going forward.

---

## Step 4b: Generate workspace files (background)

While the user is doing the real task in Step 4, OR right after Step 2 if they're slow to engage, generate these files. Use everything extracted from `profile.md` + the link fetches:

**`CLAUDE.md`** — read `.claude/context/skill-library/templates/claude-md.template.md`, fill all `{{placeholders}}`, write to workspace root replacing the bootstrap. ALL content in the client's language.

**Seed skills** — read `.claude/context/skill-library/seed-patterns/index.md`. For each applicable pattern (based on the capability areas in profile.md):
1. Read pattern SKILL.md
2. Fill `{{placeholders}}` from profile + fetched data
3. Translate names/text to client's language
4. Write to `.claude/skills/{department-folder}/{skill-name}/SKILL.md` — skills are grouped in folders by department (discovery is recursive, nesting works). The folder comes from the pattern's `department:` frontmatter: `Workspace` → `workspace/`, `Shared` → `shared/`. Never write a skill loose at `.claude/skills/{name}/`, and NEVER put non-skill files or the skill library under `.claude/skills/` — every `SKILL.md` in there is discovered as a live skill.

Always include: `save-changes`, `create-skill`, `contact-olympus`, `connect-tool`, `audit-workspace`, `ai-tips`. If Slack: also `read-slack-channel`, `post-slack-message`. If social media area: `generate-social-post`. If team leads: `one-on-one`.

**Several of these already exist** — the installer pre-creates `contact-olympus`, `connect-tool`, `audit-workspace`, `save-changes`, and `ai-tips` at `.claude/skills/workspace/`, plus `create-skill` at `.claude/skills/shared/`, in English with basic values filled (date, language, default branch, company name). Don't recreate them from scratch: personalize in place — fill remaining placeholders from the profile and, if the client's language isn't English, translate the user-facing text. `connect-tool`'s extra files (`scripts/`, `references/`), `audit-workspace`'s `references/` plus its multi-agent workflow at `.claude/workflows/workspace-audit-scan.js`, and `contact-olympus`'s `references/olympus-workspace.json` (this workspace's identity — NEVER delete, move, or regenerate it) are already in place — leave them as-is (the workflow is code, never translate it).

These base skills all carry `department: Workspace` in their frontmatter — keep it (translate the department name to the client's language along with the rest), and group them under a "Workspace" department in CLAUDE.md's "Skills by Department" section. They are never assigned to a company department.

**`.claude/context/company/company-context.md`** — populate with company name, description, departments (from profile), tools, brand voice (from fetches), and anything else extracted. Leave gaps where info is missing — they fill in through real work.

**Rewrite `GETTING-STARTED.md`** in the client's language using `.claude/context/skill-library/templates/getting-started.template.md`. Lists all the generated skills, how to use them, daily workflow, troubleshooting, glossary. Replace the bootstrap version. Always include a short plain-language "Your Olympus connection" section: the workspace sends a tiny once-a-day "everything is working" signal to the Olympus team at session start — only the date, skill count, and date of last save, never file contents or business data; `/contact-olympus` is the channel the client triggers on purpose; the files behind this (`.claude/skills/workspace/contact-olympus/references/olympus-workspace.json`, `.claude/hooks/phone-home.py`, `.claude/settings.json`) must never be deleted.

**Rewrite `README.md`** in the client's language using `.claude/context/skill-library/templates/readme.template.md`. The README is the front door — what someone sees first when they open the folder or the GitHub repo. Keep it short and never duplicate GETTING-STARTED content: one intro paragraph (what this folder is, whose it is), "start here" steps (open in the Claude Code app or VS Code, ask for what you need), the "how it works" learning loop in 4 steps (ask → it works with you → repeatable processes become shortcuts → workspace gets smarter), a pointer to `GETTING-STARTED.md` as the full guide, the "never delete `.claude`" note, and `/contact-olympus` for help. Use the assistant's name if one was chosen. Replace the bootstrap version.

**Create `.claude/shared-references/team-directory.md`** as an empty template — they fill it in as the team grows.

**Create `results/{skill-name}/` directories** for skills that produce output.

Once done, mention briefly to the user (without breaking their flow):
> "Btw, your workspace files are all set up — `CLAUDE.md`, your skills, `GETTING-STARTED.md`. Take a look whenever."

---

## Step 5: Clean up

After the first task and capture (if any):

1. Log this setup as the first entry in `.claude/logs/learning-log.md` (date, what was set up, what task was done, what was captured).
2. Delete `results/setup-progress.md` — setup is done.
3. Delete `.claude/context/skill-library/` — it's consultant scaffolding consumed by this setup (patterns + templates), not client content. Nothing in the workspace uses it after setup, and it's gitignored so it was never committed. If `/setup` is re-run later and the library is gone, personalize the existing workspace files in place instead of regenerating from patterns.
4. Keep `/setup` available in case they want to reconfigure.

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Tool auth fails (browser doesn't open) | Try once more. If still fails, skip. "No problem — we'll connect this later. Nothing's blocked." |
| Tool auth fails (browser opens, errors) | Ask them to log out of the tool in the browser, then retry. If twice fails, skip. |
| User asks to skip everything and just work | Great — go straight to Step 4. Workspace files generate in background. |
| User can't think of a task for Step 4 | Suggest based on something interesting from the link fetches: "I noticed your site mentions {X}. Want to do something around that?" Or: "Want to draft an email, summarize a doc, or check on something?" |
| User mentions a tool not in their selection | Connect it on the fly using the same flow as Step 3, then continue the task. |
| `.mcp.json` keys aren't working | Don't read the file. Ask them to double-check the values. |
| User confused by VS Code UI | "Just use this chat panel — ignore everything else." |
| Setup interrupted (user left) | `results/setup-progress.md` resumes automatically. On return: "Welcome back — picking up where we left off." |
| Internet drops mid-setup | Tool connections retry. Progress is saved. Nothing lost. |

## Anti-Patterns

- **Never re-ask what's in `profile.md`.** Name, language, links, tools — already collected.
- **Never run a long interview.** No culture/values/communication/pain-point questions. Those come out of real work.
- **Never stall on a failed tool connection.** Two attempts max, then skip and move on.
- **Never show raw error messages.** Translate: "Something didn't work" + what to do next.
- **Never read `.mcp.json` or `.env`.** They contain secrets. Ask the user to verify values themselves.
- **Never make the user wait for workspace generation.** Do it in the background while they're working in Step 4.
- **Never overwhelm with multiple questions at once.** One at a time, multiple-choice when possible.

