---
name: contact-olympus
description: Talk to your Olympus AI team — send a workspace health report, or send a question, idea, or bug report (they respond by email within 24 hours). Use after a significant work session or weekly with "send report", "report to olympus", "update consultants", or whenever something isn't working or you have feedback with "ask olympus", "send feedback", "report a bug", "contact support".
metadata:
  maintainer: All Teams
  last-updated: 2026-07-03
  department: Workspace
---

# Contact Olympus — Talk to Your Consulting Team

This skill is the channel between this workspace and the Olympus AI team that supports it. It does two things:

- **Send a health report** — a summary of workspace activity so the team can proactively help you improve
- **Send a message** — a question, idea, or bug report; the team responds to your email

## Which one does the user want?

- "send report", "report to olympus", "update consultants", "report status" → **Flow A: Health Report**
- "ask olympus", "send feedback", "report a bug", "I have a question", "contact support" → **Flow B: Message**
- Unclear → ask with `AskUserQuestion`: "Do you want to send a workspace health report, or a question/feedback for the team?"

## Workspace Identity

This workspace's identity lives in `.claude/skills/workspace/contact-olympus/references/olympus-workspace.json` (written when the workspace was installed). Both flows read `session_code` and the endpoint from it at runtime — this skill does **not** use `{{session_code}}` / endpoint placeholders. The only placeholder is `2026-07-03` in the frontmatter, filled by `/setup`.

If that file is missing, this workspace has no link to the Olympus team — tell the user to email `atlas@olympus-ai.xyz` directly instead.

---

## Flow A: Health Report

### What Gets Reported

This is transparent — here's exactly what we send:
- **Skills created or modified** since last report
- **Learning log entries** (processes captured, gaps identified)
- **Activity level** (how much the workspace is being used)
- **Issues or friction** (things that didn't work well)

We do NOT send your proprietary data, files, or conversation content.

### Step A1: Collect Information

Read the following files and summarize what happened since the last report:

1. **Learning log** — Read `.claude/logs/learning-log.md`. Extract:
   - New entries since last report (look for dates after the last report date)
   - Skills captured (count and names)
   - Skills modified (count and names)
   - Gaps identified (things the workspace couldn't do)
   - Friction points (things that were confusing or slow)

2. **Skills directory** — List `.claude/skills/*/SKILL.md`. Count total skills vs. seed skills.

3. **Recent git activity** — Run `git log --oneline -20` to gauge activity level.

### Step A2: Build Report Payload

Structure the report as JSON:

```json
{
  "period": "2026-03-15 to 2026-03-22",
  "skills_created": ["skill-name-1", "skill-name-2"],
  "skills_modified": ["existing-skill"],
  "total_skills": 12,
  "seed_skills": 6,
  "captured_skills": 6,
  "activity_level": "active",
  "learning_log_entries": 5,
  "gaps": ["Couldn't connect to HubSpot", "No skill for invoice generation"],
  "friction": ["Slack auth expired mid-session"],
  "notes": "Team is actively using the workspace for sales pipeline management"
}
```

Activity levels: `active` (daily use), `moderate` (weekly use), `low` (less than weekly), `inactive` (no recent activity).

### Step A3: Send Report

```bash
CONFIG=.claude/skills/workspace/contact-olympus/references/olympus-workspace.json
SESSION=$(python3 -c "import json;print(json.load(open('$CONFIG'))['session_code'])")
ENDPOINT=$(python3 -c "import json;print(json.load(open('$CONFIG'))['report_endpoint'])")

curl -s -X POST "$ENDPOINT" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "'"$SESSION"'",
    "report_type": "learning_log",
    "content": <the JSON from Step A2>
  }'
```

### Step A4: Confirm

Tell the user:
- "Report sent to your Olympus AI team. They'll review it and reach out if they spot anything that needs attention."
- Show a brief summary of what was sent (skills created, gaps, friction points)
- Save the current date as the last report date in `.claude/context/last-report.txt`

### Note on Automatic Reporting

A `SessionStart` hook (`.claude/hooks/phone-home.py`) already sends a lightweight daily activity ping automatically — the client never has to remember to do it. This health report is the **richer, manual** report: run it after a meaningful work session, or weekly, to send the full learning-log summary.

---

## Flow B: Question, Feedback, or Bug Report

### Step B1: Collect Information

To respond, the team needs name, email, type, and message. Ask the user for whatever they haven't already provided — if it's in their message, don't ask again, just confirm what you understood.

1. **Name** — "What's your name?"
2. **Email** — "What email should we respond to?"
3. **Type** — "Is this a question, feedback, or a bug report?"
   - `question` — You need help or want to know how to do something
   - `feedback` — You have a suggestion, idea, or general comment
   - `bug` — Something is broken or not working as expected
4. **Message** — "What would you like to tell the team?"

If the type is `bug`, also ask:
- "What were you trying to do when this happened?"
- "What did you expect to happen vs. what actually happened?"

Compose the message including all the context. For bugs, format it as: what they did → what they expected → what happened.

### Step B2: Confirm Before Sending

Show the user a summary of what will be sent:

```
Type: [question/feedback/bug]
From: [name] ([email])
Message: [their message]
```

Ask: "Does this look right? I'll send it to the Olympus AI team."

### Step B3: Send

```bash
CONFIG=.claude/skills/workspace/contact-olympus/references/olympus-workspace.json
SESSION=$(python3 -c "import json;print(json.load(open('$CONFIG'))['session_code'])")
ENDPOINT=$(python3 -c "import json;print(json.load(open('$CONFIG'))['feedback_endpoint'])")

curl -s -X POST "$ENDPOINT" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "'"$SESSION"'",
    "type": "<question|feedback|bug>",
    "message": "<the composed message>",
    "sender_name": "<their name>",
    "sender_email": "<their email>"
  }'
```

### Step B4: Confirm

Tell the user:
- "Sent! The Olympus AI team will respond to [email] within 24 hours."
- If it was a bug: "In the meantime, here's a workaround if I can think of one..." — try to help them with whatever they reported.

---

## Anti-Patterns

- **Never delete, move, or edit `references/olympus-workspace.json`** — it's this workspace's identity; without it both flows (and the daily heartbeat) lose their link to the Olympus team
- **Don't send a message without showing the user the summary first** — always confirm before sending
- **Don't include proprietary data in health reports** — only the metadata listed in "What Gets Reported"
