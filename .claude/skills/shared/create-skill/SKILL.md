---
name: create-skill
description: Create or improve skills (slash commands) for the Clomatica agents workspace with proper SKILL.md structure, frontmatter, references, and department organization. Use this skill whenever the user wants to add a new reusable workflow, automate a repeated task, turn an ad-hoc process into a skill, or update/improve an existing skill. Trigger phrases include "create a skill", "new slash command", "I want a skill for", "make a skill", "add a skill", "turn this into a skill", "automate this workflow", "update a skill", "improve a skill", "optimize skill description". Wraps the official skill-creator with Clomatica-specific conventions (frontmatter rules, department placement, CLAUDE.md updates).
metadata:
  maintainer: All Teams
  last-updated: 2026-07-03
  department: Shared
---

# Create Skill

Create or improve skills for the Clomatica agents workspace by delegating to the official `/skill-creator`, then applying Clomatica-specific conventions and validation on top.

## When to Use

**Invoke this skill when:**
- The user explicitly asks to create a skill (e.g., "create a skill for X", "I want a new slash command")
- The user wants to update, improve, or optimize an existing skill
- The user runs `/create-skill`

**Proactively suggest this skill when:**
- The user describes a repeatable workflow that would benefit from being a skill
- The user asks for help with a task that doesn't have a skill but should
- The user mentions doing the same thing frequently

In these cases, ask: "This sounds like it could be a useful skill. Would you like me to create a `/skill-name` skill so you can reuse this workflow?"

## Prerequisites

Before starting, read the reference file for detailed patterns and examples:
- `.claude/skills/shared/create-skill/references/skill-creation-guide.md`

## Workflow

### Step 0: Check Installed Plugins First

Before building anything, check if an existing plugin already covers the need:

1. **List installed plugins:** Run `claude plugin list --json` and review what's already available.
2. **List available plugins:** Run `claude plugin list --available --json` and check if any marketplace plugin fits the use case.
3. **If a match exists:**
   - If already installed → tell the user they can use it directly (show the slash commands it provides).
   - If available but not installed → install it with `claude plugin install {plugin-name}@{marketplace} --scope project` and confirm it works.
   - Skip the rest of this skill — no need to build what already exists.
4. **If no match exists** → proceed to Step 1 below to create a custom skill.

**If a plugin covers only part of the use case**, the new skill should **reference and wrap the plugin** rather than reinvent its methodology: use the plugin for the general-purpose part (spec structure, metrics analysis, SQL optimization), add Clomatica-specific value on top (context loading, output conventions, domain knowledge, guardrails), and add the plugin to the skill's `## Related Skills` table with a note on what it provides.

This prevents reinventing the wheel. Plugins are maintained upstream and get updates automatically — always prefer them over custom skills when the fit is good.

### Step 1: Define the Use Case

Before writing anything, identify 2-3 concrete use cases the skill should enable. Ask the user:

- What does the user want to accomplish?
- What multi-step workflows does this require?
- Which tools are needed (built-in or MCP)?
- What domain knowledge or best practices should be embedded?
- **Does it fan out over a work-list?** Does the skill repeat the same independent operation over many units (clients, repos, prospects, channels, doc sections, schedules) or gather from many sources concurrently? If so, plan a `## Parallel Execution (Workflow)` section (see Step 3, section order) so the skill orchestrates the fan-out with the **Workflow tool** instead of a serial loop.

Use `AskUserQuestion` with these options:
- **Skill category**: Document & Asset Creation | Workflow Automation | MCP Enhancement
- **Department**: list the existing department folders under `.claude/skills/` (plus CLAUDE.md's Skills by Department) as options, and always include "New department". `workspace/` is reserved for the base skills — never offer it.

### Step 2: Run the Official Skill Creator

Invoke the official `/skill-creator` skill to generate or improve the skill. It handles the full draft → test → evaluate → iterate loop, including:
- Drafting the initial SKILL.md
- Running test cases and showing you results in a browser viewer
- Iterating based on your feedback
- Optionally optimizing the description for better triggering accuracy

Let `/skill-creator` finish before proceeding to Step 3.

### Step 3: Apply Clomatica-Specific Conventions

After `/skill-creator` finishes, verify and fix the skill against Clomatica workspace requirements. The official creator doesn't know about our conventions — this step is essential.

#### 3a. Directory Placement

The skill must be under `.claude/skills/{department}/` — skills are grouped in folders by department:
- `{department}/` — one folder per company department (check existing folders under `.claude/skills/` and CLAUDE.md's Skills by Department; create the folder if the user picks a new department)
- `shared/` — cross-team utilities used by everyone (e.g. this skill, Slack helpers)
- `workspace/` — RESERVED for the base skills that manage the workspace itself. Never place new skills here.

#### 3b. YAML Frontmatter

The frontmatter is how Claude decides whether to load the skill — it's the most important part. It's always loaded into Claude's system prompt (first level of progressive disclosure).

**Required fields:**

```yaml
---
name: skill-name-in-kebab-case
description: What it does. Use when user says "trigger phrase 1", "trigger phrase 2". Do NOT use for X (use other-skill instead).
metadata:
  maintainer: Department Team
  last-updated: YYYY-MM
  department: Department
---
```

**Rules:**
- `name`: kebab-case only. No spaces, capitals, or underscores. Must match folder name.
- `description`: Follow this structure: `[What it does] + [When to use it] + [Key capabilities]`. Under 1024 characters. Must include specific trigger phrases users would actually say. Add "Do NOT use for..." to disambiguate from similar skills. Mention relevant file types if applicable.
- No XML angle brackets (`<` or `>`) anywhere in frontmatter — security restriction
- No "claude" or "anthropic" in the skill name — reserved prefixes

**Good description examples:**
```
# Good - specific and actionable
description: Analyzes production database issues and traces records through the pipeline. Use when user says "investigate data", "trace a record", "find missing payouts".

# Good - includes negative triggers
description: Build SQL queries against the production database. Use when user says "build a query", "write SQL", "query the DB". Do NOT use for running queries (use query-postgres instead).
```

**Bad description examples:**
```
# Too vague
description: Helps with projects.

# Missing triggers
description: Creates sophisticated multi-page documentation systems.

# Too technical, no user triggers
description: Implements the Project entity model with hierarchical relationships.
```

**Optional frontmatter fields** (use when relevant):
- `allowed-tools`: Restrict which tools the skill can use (e.g., `"Bash(python:*) WebFetch"`)
- `compatibility`: Environment requirements (1-500 chars, e.g., "Requires psql CLI")
- `license`: For open-source skills (MIT, Apache-2.0)
- Additional metadata: `version`, `mcp-server`, `category`, `tags`

#### 3c. Skill Content — Progressive Disclosure

Skills use a three-level progressive disclosure system to minimize token usage:

1. **First level (YAML frontmatter)** — Always loaded in Claude's system prompt. Provides just enough info to know WHEN to load the skill.
2. **Second level (SKILL.md body)** — Loaded when Claude thinks the skill is relevant. Contains the full instructions and guidance.
3. **Third level (Linked files)** — Additional files in the skill directory (`references/`, `scripts/`, `assets/`) that Claude can choose to navigate and discover as needed.

**CRITICAL: Keep SKILL.md under 5,000 words.** Move detailed documentation, templates, long examples, and reference material to `references/` files and link to them. This prevents context bloat when the skill loads.

#### 3d. Standard Section Order

Use this order (required sections marked with \*):

1. `# Skill Name` \* — Brief description of what the skill does
2. `## When to Use` — Trigger conditions and proactive suggestions
3. `## Prerequisites` — What's needed before running (context files to read, tools needed, env vars)
4. `## Workflow` / `## Steps` \* — Numbered steps with clear, specific, actionable instructions
5. `## Parallel Execution (Workflow)` — **Add this when the skill fans out over a work-list** (many independent clients/repos/prospects/channels/sections, or multi-source concurrent gathering). Place it right after the main steps. Document: the concrete fan-out **Shape** (using the skill's real step names), how to build the **work-list** inline before fanning out, **concurrency & batching** (wave size to respect API/MCP rate limits, ~16 concurrent cap), **error handling** (which per-item failures are non-blocking via `.filter(Boolean)`), and **sequential gates** (any human-confirm / approval / production-write step that must stay sequential and run after the fan-out). See `references/skill-creation-guide.md` for details. Skip for interactive, single-unit, or single-action skills — orchestration overhead isn't worth it there.
6. `## Output` — What the skill produces, where it saves (must be `results/{subdirectory}/`)
7. `## Example Interactions` \* — 1-3 concrete user-Claude interaction examples
7. `## Anti-Patterns` — What NOT to do
8. `## Troubleshooting` — Common errors with cause and solution
9. `## Self-Improvement` — When/how to update this skill after use
10. `## Related Skills` — Table of skills that complement this one
11. `## Context Files` \* — List of `.claude/context/` files to read

#### 3e. Writing Best Practices

- **Be specific and actionable** — "Run `python scripts/validate.py --input {filename}` to check data format" is good. "Validate the data before proceeding" is bad.
- **Put critical instructions at the top** — Use `## Important` or `## Critical` headers. Repeat key points if needed.
- **Use bullet points and numbered lists** — Not prose paragraphs
- **Reference bundled resources clearly** — "Before writing queries, consult `references/api-patterns.md` for rate limiting guidance"
- **Include error handling** — For each step, what can go wrong and how to fix it
- **Add explicit encouragement for thoroughness** — "Take your time to do this thoroughly. Quality is more important than speed. Do not skip validation steps."
- **Questions must use multiple choice** — All user questions use `AskUserQuestion` with predefined options (never open-ended numbered lists)

#### 3f. File Structure

A skill folder can contain:
```
your-skill-name/
├── SKILL.md                    # Required - main skill file
├── scripts/                    # Optional - executable code (Python, Bash, etc.)
│   ├── process_data.py
│   └── validate.sh
├── references/                 # Optional - documentation loaded as needed
│   ├── api-guide.md
│   └── examples/
└── assets/                     # Optional - templates, fonts, icons used in output
    └── report-template.md
```

**Important:**
- File must be exactly `SKILL.md` (case-sensitive). No variations (SKILL.MD, skill.md, etc.)
- Do NOT include a README.md inside the skill folder — all documentation goes in SKILL.md or references/
- Folder name must be kebab-case: `notion-project-setup` not `Notion Project Setup` or `notion_project_setup`

#### 3g. Output Location

If the skill produces a file, it **must** save to `results/{subdirectory}/`. Create the subdirectory if needed and document the path in the SKILL.md.

### Step 4: Run Validation Checklist

Before finalizing, verify every item:

**Structure & Naming:**
- [ ] Folder at `.claude/skills/{department}/{skill-name}/` (2-level nesting, no extra grouping dirs)
- [ ] Folder named in kebab-case, matches `name` field
- [ ] SKILL.md file exists (exact case-sensitive spelling)
- [ ] SKILL.md under 5,000 words (detailed content moved to references/)

**YAML Frontmatter:**
- [ ] Has `---` delimiters (opening and closing)
- [ ] `name`: kebab-case, no spaces, no capitals, no "claude"/"anthropic"
- [ ] `description` includes: WHAT it does + WHEN to use (trigger phrases) + "Do NOT use for..." (negative triggers)
- [ ] `description` under 1024 characters
- [ ] No XML angle brackets (`<` or `>`) in any frontmatter value
- [ ] `metadata.last-updated` set to current YYYY-MM
- [ ] `metadata.department` matches folder department

**Required Sections (in order):**
- [ ] `# Skill Name` — brief description
- [ ] `## Workflow` / `## Steps` — numbered, specific, actionable steps
- [ ] `## Example Interactions` — 1-3 concrete user-Claude exchanges
- [ ] `## Context Files` — list of `.claude/context/` files to read

**Recommended Sections:**
- [ ] `## Parallel Execution (Workflow)` — present if the skill fans out over a work-list (clients/repos/prospects/channels/sections) or gathers from many sources; documents Shape, work-list, batching, error handling, and sequential gates
- [ ] `## Anti-Patterns` — what NOT to do
- [ ] `## Troubleshooting` — table with Problem | Cause | Fix columns
- [ ] `## Self-Improvement` — instructions to update skill after use
- [ ] `## Related Skills` — table of complementary skills with "Do NOT use for" cross-refs

**Quality Checks:**
- [ ] Instructions are specific and actionable (not vague "validate the data")
- [ ] All user questions use `AskUserQuestion` with multiple choice (not open-ended lists)
- [ ] Output location documented (must be `results/{subdirectory}/` if applicable)
- [ ] Skill name doesn't duplicate an existing skill (check CLAUDE.md Skills by Department)
- [ ] Negative triggers disambiguate from similar skills (prevents cross-triggering)

**Database Query Checks (if skill uses SQL):**
- [ ] SQL queries are in `references/` files, not inline in SKILL.md
- [ ] SELECT queries delegate to `/query-postgres` (never call psql or run_query.sh directly from the skill)
- [ ] Write queries (UPDATE, DELETE, INSERT) have an "Admin required" note — the skill must present the filled-in query to the user and tell them an admin must run it on the production database. Never attempt to execute write queries.

### Step 5: Update CLAUDE.md

Add the new skill to the **Skills by Department** table in `CLAUDE.md` under the appropriate department section with a one-line description.

### Step 6: Confirm Creation

Tell the user:
- Skill directory created at: `.claude/skills/{department}/{skill-name}/SKILL.md`
- Skills are auto-discovered by Claude Code (no registration needed)
- They can now use it with `/{skill-name}`
- Suggest testing: "Try running `/{skill-name}` with a real task to verify it triggers and executes correctly"

## Example Interactions

**Example 1: User explicitly asks**
```
User: "Create a skill for reviewing client invoices"
Claude: Asks about skill category and department via AskUserQuestion.
        Invokes /skill-creator to draft, test, and iterate on the SKILL.md.
        After skill-creator finishes, applies Clomatica conventions (frontmatter, placement).
        Verifies against checklist. Saves under customer-success/review-invoices/.
        Updates CLAUDE.md. Confirms to user with test suggestion.
```

**Example 2: Proactive suggestion**
```
User: "Can you check if the exchange rates synced correctly today?"
Claude: [completes the task, then notices this is a repeatable workflow]
Claude: "This seems like a workflow you might run regularly. Want me to create a
        /check-exchange-rates skill so you can reuse it?"
```

**Example 3: Complex multi-MCP skill**
```
User: "Create a skill that fetches Linear issues, formats a report, and posts to Slack"
Claude: Identifies this as a Workflow Automation category spanning multiple MCPs.
        Asks about department placement. Invokes /skill-creator to draft and test.
        skill-creator structures workflow with Fetch -> Format -> Post phases.
        After iteration, applies Clomatica conventions and moves report template to references/.
        Updates CLAUDE.md. Confirms with test suggestion.
```

**Example 4: Improving an existing skill**
```
User: "Can we improve the /query-postgres skill?"
Claude: Invokes /skill-creator with the existing SKILL.md path.
        skill-creator runs evals on the current version vs improvements.
        After user reviews results, applies Clomatica-specific validation.
        Pushes changes via /save-changes.
```

## Anti-Patterns

- **Don't create a skill without YAML frontmatter** — Every skill needs `name`, `description`, and `metadata` in the `---` delimited block
- **Don't skip the description trigger phrases** — Without them, Claude can't auto-detect when the skill is relevant
- **Don't write vague instructions** — "Validate the data" is bad. "Run `python scripts/validate.py --input {filename}` to check data format. If validation fails, common issues include: missing required fields, invalid date formats (use YYYY-MM-DD)" is good.
- **Don't create overly broad skills** — If it does too much, split into multiple focused skills
- **Don't duplicate existing skills** — Always check the Skills by Department table in CLAUDE.md first
- **Don't build what a plugin already does** — Always run Step 0 (check plugins) before creating a custom skill. Plugins get upstream updates; custom skills don't.
- **Don't put everything in SKILL.md** — Move templates, detailed reference docs, and long examples to `references/` files. Keep SKILL.md under 5,000 words.
- **Don't include README.md in the skill folder** — All documentation goes in SKILL.md or references/
- **Don't use ambiguous language** — "Make sure to validate things properly" is bad. "CRITICAL: Before calling create_project, verify: project name is non-empty, at least one team member assigned, start date is not in the past" is good.

## Troubleshooting

### Skill Won't Upload / Not Detected
**Cause:** File not named exactly `SKILL.md` (case-sensitive), or missing `---` delimiters in frontmatter.
**Fix:** Rename to exactly `SKILL.md`. Verify frontmatter has opening and closing `---`.

### Skill Doesn't Trigger Automatically
**Symptom:** Skill never loads unless user types `/skill-name`.
**Cause:** Description is too vague or missing trigger phrases.
**Fix:** Revise description to include specific tasks users would say. Check:
- Is it too generic? ("Helps with projects" won't work)
- Does it include trigger phrases users would actually say?
- Does it mention relevant file types if applicable?
**Debug:** Ask Claude "When would you use the [skill name] skill?" — Claude will quote the description back. Adjust based on what's missing.

### Skill Triggers Too Often
**Symptom:** Skill loads for unrelated queries.
**Fix:**
1. Add negative triggers: "Do NOT use for simple data exploration (use data-viz skill instead)"
2. Be more specific in description
3. Clarify scope: "Use specifically for online payment workflows, not for general financial queries"

### Instructions Not Followed
**Symptom:** Skill loads but Claude doesn't follow the steps.
**Common causes:**
1. Instructions too verbose → keep concise, use bullet points
2. Instructions buried → put critical instructions at the top with `## Important` headers
3. Ambiguous language → be specific with explicit validation criteria
4. Model skipping steps → add "Take your time. Quality is more important than speed. Do not skip validation steps."

### Skill Seems Slow or Degraded
**Cause:** SKILL.md too large, loading too much content into context.
**Fix:** Keep SKILL.md under 5,000 words. Move detailed docs to `references/` and link to them.

## Self-Improvement

After creating or improving a skill with this workflow, check:
- Did `/skill-creator` produce output that violated a Clomatica convention? If so, add it to the Step 3 checklist.
- Did a new frontmatter field become relevant? Add it to the optional fields list.
- Did a new department or subdirectory structure emerge? Update the directory placement section.
- Was the validation checklist missing an item? Add it.

## Related Skills

| Skill | Relationship |
|-------|-------------|
| `/save-changes` | Push the new skill to the remote after creation |
| `/audit-workspace` | Audit the workspace (including CLAUDE.md) after adding new skill entries |

## Context Files

- `CLAUDE.md` — Workspace conventions, Skills by Department table, Contributing section
- `.claude/skills/shared/create-skill/references/skill-creation-guide.md` — Detailed patterns, description examples, testing approach
