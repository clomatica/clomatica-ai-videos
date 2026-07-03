---
name: consulting
description: Deep-dive interview about the company — culture, values, team, how work flows, pain points. Use when the user says "tell me about my company", "do the consulting", "/consulting", or wants the assistant to understand their business better before working. Not part of the initial setup — this runs on demand whenever the user is ready.
---

# Consulting — Deep-Dive Company Interview

A structured conversation to understand the company deeply. The output is saved to the workspace context files so every future task benefits.

Use when the user explicitly asks for it. Not part of `/setup`.

## Principles

- Use `AskUserQuestion` for EVERY question. Multiple-choice when possible, free text as last option.
- **One question at a time.** Never overwhelm.
- **Listen 80%, talk 20%.** Let them describe things in their own words.
- **Never re-ask what's already in `.claude/context/company/`** — check first, confirm only if stale.
- **Follow the arc:** Desired State → Pain Points → Current State. Dreams first, problems second, facts last.
- If they don't know an answer, skip. Gaps are fine — they fill in with real work.

## Before starting

1. Read `.claude/context/company/profile.md` and `company-context.md`.
2. Note what's already known — don't re-ask any of it.
3. Tell the user:
> "I'll ask a handful of questions to understand your company better. Takes about 10 minutes. You can stop anytime and pick up later by running `/consulting` again. Ready?"

Wait for confirmation.

---

## Step 1: Import more context

Ask:
> "Do you have any docs I can read — brand guide, employee handbook, onboarding docs, product specs? The more I can read, the fewer questions I need to ask."

If yes: fetch them (`WebFetch` for URLs, or ask them to paste/drop the file). Extract everything useful. Skip any question below that's already answered.

Context sources worth asking for:

| Source | What to extract |
|--------|----------------|
| Notion wiki / handbook | Values, org chart, processes, brand guidelines |
| Brand guide (PDF/doc) | Tone of voice, communication style |
| Employee handbook | Values, policies, structure |
| Onboarding docs | What new hires learn |
| Product docs / API | Technical context, features |
| GitHub READMEs | What they build, contributing norms |

## Step 2: Who uses this workspace

> "Besides you, who on your team will use this workspace? What do they do?"

Shapes seed skills, department structure, permissions.

## Step 3: Main pain point

> "What's the one thing your team spends too much time on that you'd love to speed up?"

The #1 signal for skill prioritization. Don't dig deeper — the rest surfaces through real work.

## Step 4: Organization

Skip anything already in profile.md or extracted in Step 1.

1. **Departments** — confirm or expand on what profile.md has.
2. **Culture & values** — "How would you describe your company's culture? Do you have defined values?"
3. **Communication style** — "How does your team communicate? Mostly Slack? Meetings? Async?"
4. **Decision-making** — "How do decisions get made? Centralized, distributed, by team?"

## Step 5: What's working

> "What's working really well right now that you DON'T want me to disrupt?"

Critical — prevents the workspace from breaking things that are already good.

## Step 6: Desired future state

> "If this workspace is wildly successful in 3 months, what's different? What are the quick wins you'd love to see?"

---

## Step 7: Save everything

Update `.claude/context/company/company-context.md` with all new data:
- Team members and roles
- Departments with main tasks
- Culture and values
- Brand voice
- Decision-making style
- Communication style
- Pain points and priorities
- What's working well (protect list)
- Desired future state

Update `.claude/context/company/profile.md` if anything new came up.

Update `.claude/shared-references/team-directory.md` with any team members mentioned.

If they shared SOPs or process docs, convert each to a captured skill using `/create-skill`.

---

## Step 8: Confirm and offer next action

Show them a quick summary:
> "Got it. I've updated your workspace with:
> - [list of updates]
>
> Want to do something with this new context now? Or we can stop here and it'll kick in next time you ask for something."

If they want to work: pick up from their pain point or desired quick wins.

If they stop: log to `.claude/logs/learning-log.md` and end.

---

## Anti-Patterns

- **Never re-ask what's in profile.md or company-context.md.** Check before asking.
- **Never ask more than one question at a time.**
- **Never dig into pain points.** One pain-point question, then move on. Depth comes from real work.
- **Never block on missing answers.** "I don't know" is a valid response — skip.
- **Never read `.mcp.json` or `.env`.** They contain secrets.

