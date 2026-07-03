---
name: audit-workspace
description: Full workspace health audit — optimize CLAUDE.md, detect duplicate content across skills and context files, check for new plugins and automations, evaluate skill quality, and verify workspace hygiene. Use when the user says "audit", "audit my workspace", "check my workspace", "workspace health", "what can be improved", or when the scheduled reminder triggers. Do NOT use for building new skills — see /create-skill.
metadata:
  maintainer: All Teams
  last-updated: 2026-06
  department: Workspace
  frequency: configurable (default monthly)
---

# Audit Workspace

Comprehensive workspace health audit in 5 phases. Keeps the workspace lean, consistent, and up-to-date:

1. **CLAUDE.md Optimization** — Trim, deduplicate, and improve the root CLAUDE.md
2. **Duplicate Detection** — Find redundant content across skills, context files, and CLAUDE.md
3. **Automation & Plugin Adoption** — Check installed plugins, scan the marketplaces, run the automation recommender, recommend what to adopt
4. **Skill Quality Evaluation** — Score skills changed since the last audit (runs after Phase 3 so it scores skills post-updates)
5. **Workspace Hygiene** — Verify internal links, detect orphaned context files, check context freshness, validate tool dependencies

The two heavy phases (2 and 4) run through a bundled multi-agent workflow — see [Execution Model](#execution-model-multi-agent-workflow).

## When to Use

- On the configured schedule (default: monthly — see [Audit Frequency](#audit-frequency)). Claude reminds the user proactively.
- When the user asks to audit, optimize, or improve the workspace
- After a major change (new department, new team members, new tools)

## Output

- `results/workspace-audit/YYYY-MM-DD-audit.md` — Full dated report for each run
- `.claude/logs/audit-log.md` — Lightweight index of all runs with links, the Commit SHA for incremental Phase 4 diffs, dismissed findings, and the next-due date
- `results/workspace-audit/skill-quality-report-{YYYY-MM-DD}.md` — Phase 4 skill scores (kept per-run for comparison)
- `results/workspace-audit/plugin-report-{YYYY-MM-DD}.md` — Phase 3 findings
- `results/workspace-audit/phase2-duplicates.md` — Phase 2 intermediate results (overwritten each run)

Phase 1 and 2 fixes are applied directly to the affected files after user approval. See `references/audit-log-template.md` for report and index formats.

**This is a non-technical client workspace.** Every report and question shown to the user must be in plain language and in the workspace's language — no jargon like "frontmatter", "SHA", or "MCP server". Translate findings into what they mean for the user's work.

## Step 0: Check Audit History

Read `.claude/logs/audit-log.md`:
- When was the last audit? What was found?
- Which findings did the user dismiss? **Never re-raise a dismissed finding** unless something changed.
- Take the most recent entry's **Commit** SHA — Phase 4 uses it as the incremental diff base.

If the file doesn't exist, this is the first audit — create it from the index format in `references/audit-log-template.md` and run Phase 4 as a full scan.

---

## Phase 1: CLAUDE.md Optimization

**Goal:** Keep the root CLAUDE.md concise, accurate, and matched to what's actually in the workspace.

### Step 1.1: Check for Stale Content

Read `CLAUDE.md` and check:

- **Skills table accuracy** — Glob `.claude/skills/**/SKILL.md` and compare against the skills tables in CLAUDE.md. Flag missing or removed skills.
- **Context files accuracy** — Glob `.claude/context/**/*.md` and compare against any context listing. Flag missing or new files.
- **Stale instructions** — References to skills, context files, directories, or tools that no longer exist on disk or are no longer connected.
- **Redundancy with skills** — CLAUDE.md should hold only the skill name + one-line description, not workflow details that already live in a SKILL.md.

### Step 1.2: Run the CLAUDE.md Improver

Invoke `claude-md-management:claude-md-improver` on the workspace root `CLAUDE.md` only. Collect its quality score and recommendations — do NOT let it auto-apply changes; all edits go through Step 1.3.

### Step 1.3: Propose and Apply

Consolidate Step 1.1 + 1.2 findings into one plain-language summary: what to remove, what to update (before/after), what to add. Apply clearly-safe fixes yourself (mismatched skill index, outdated directory listing). For the rest, use `AskUserQuestion`:
- **Apply all changes** / **Review one by one** / **Skip this phase**

Verify the result is valid markdown and that no skill entry still in use was removed.

---

## Phase 2: Duplicate Detection

**Goal:** Find redundant content across skills, context files, and CLAUDE.md to prevent drift.

### Duplicate Definitions

- **Exact duplicate:** Identical text (same query, same paragraph, same steps) in multiple files
- **Near-duplicate:** Same content with minor variations
- **Semantic duplicate:** Same intent expressed differently — do NOT flag, too subjective

Only flag exact and near-duplicates appearing in **3+ locations** (2 = reasonable cross-reference; 3+ = drift risk). Compare blocks of **5+ consecutive identical lines**.

### Step 2.1: Cross-Department Scan

**Primary path — run the `workspace-audit-scan` workflow** (see [Execution Model](#execution-model-multi-agent-workflow)). It discovers the department folders under `.claude/skills/`, fans out one read-only agent per department, and returns a `duplicates` array already tallied to the 3+-location threshold. Write that array to `results/workspace-audit/phase2-duplicates.md`.

**Inline fallback** (small workspace — 1–2 departments or under ~10 skills, where workflow overhead isn't worth it): scan one department directory at a time, writing intermediate results to `phase2-duplicates.md`. Per department, check:

- **A. Query duplication:** Grep for `SELECT.*FROM` (and similar query patterns) in that department's `*.md` files
- **B. Workflow instruction duplication:** copy-pasted multi-step instructions (5+ identical lines) referencing shared skills (`save-changes`, `connect-tool`, etc.)
- **C. Context content embedded in skills:** blocks of 5+ lines replicating `.claude/context/company/` or `.claude/shared-references/` content

### Step 2.2: Verify Content, Then Report

**MANDATORY before classifying anything as actionable — read the actual flagged blocks.** The detector fingerprints on a normalized key, so it WILL match a **shared template applied per-skill** (same headings, different content). Open each flagged group and classify:
- **Drift risk (actionable):** blocks are exact/near-verbatim in 3+ files → extract
- **Template-consistency (NOT actionable):** shared structure but content parameterized per skill → leave as-is, report as "template, left alone"

### Step 2.3: Apply Fixes

For each approved fix: extract the duplicated content to the right shared location (context file or shared reference), replace inline copies with a link, verify no information is lost. Use `AskUserQuestion`:
- **Fix all duplicates** / **Review one by one** / **Skip this phase**

---

## Phase 3: Automation & Plugin Adoption

**Goal:** Review installed plugins, scan the marketplace catalogs, run the automation recommender, and recommend what to adopt.

### Step 3.1: List Installed Plugins

```bash
claude plugin list
```

If the `anthropics/knowledge-work-plugins` marketplace is not configured, add it:
```bash
claude plugin marketplace add anthropics/knowledge-work-plugins
```

### Step 3.2: Scan Marketplace Plugins

1. List and refresh configured marketplaces:
   ```bash
   claude plugin marketplace list
   claude plugin marketplace update
   ```
2. Enumerate every available plugin by reading each marketplace manifest:
   ```bash
   cat ~/.claude/plugins/marketplaces/{marketplace-name}/.claude-plugin/marketplace.json
   ```
3. Split into three buckets: **installed & enabled**, **installed but disabled**, **not installed**. A disabled plugin is never an install recommendation — if any workspace skill references a disabled plugin (grep skills for `{plugin}:` references), flag it as a health issue ("dependency disabled — skill X is degraded").
4. **Check the profile** at `.claude/context/company/profile.md`, section "Recommended Plugin Skills" — are all recommended plugins installed? Flag missing ones.
5. From the not-installed bucket, recommend only plugins that map to a real need in THIS workspace (look at departments, connected tools, and recent activity in `.claude/logs/learning-log.md`). Do not flag every uninstalled plugin — most are irrelevant.

### Step 3.3: Plugin-vs-Skill Overlap

If a custom skill does the same thing as an installed plugin, suggest switching to the plugin (it's maintained automatically). Archive the custom skill only if the user agrees.

### Step 3.4: Run the Automation Recommender

Invoke `claude-code-setup:claude-automation-recommender` on the workspace. If it's not available:
```bash
claude plugin install claude-code-setup
```
(then reload Claude Code; if it still fails, skip this step and note it in the log).

**Filter its recommendations before showing the user:**
- Drop anything that asks the client to write code, edit config files, or run commands themselves
- Translate each kept recommendation into plain language in the workspace's language — "a reminder that runs when you finish a task", not "a Stop hook"
- Cross-check `.claude/logs/audit-log.md` — don't re-raise anything the user already declined

### Step 3.5: Report

Save findings to `results/workspace-audit/plugin-report-{YYYY-MM-DD}.md` (installed plugins, recommended plugins with the need each serves, skills that could leverage plugin agents, automation recommendations). Then use `AskUserQuestion`:
- **Apply recommended additions** / **Just log the report** / **Skip this phase**

Apply the safe, obvious ones yourself (e.g., a recommended plugin from the profile that was never installed). Never auto-install beyond what the user approved.

---

## Phase 4: Skill Quality Evaluation

**Goal:** Evaluate skills using the `/skill-creator` plugin. Runs last among the scan phases so it scores skills after Phase 3 updates.

### Step 4.1: Inventory Skills Changed Since the Last Audit

Phase 4 is **incremental** — evaluate only skills changed since the previous audit, not all of them every time. The `workspace-audit-scan` workflow self-computes this (a scout agent runs the procedure below); you only build it by hand on the inline fallback path:

1. **Find the diff base.** Take the **Commit** SHA from the most recent `.claude/logs/audit-log.md` entry.
2. **List changed skills** (including uncommitted and brand-new ones):
   ```bash
   BASE=<sha from the last audit-log entry>
   { git diff --name-only "$BASE" -- .claude/skills/ ;
     git ls-files --others --exclude-standard .claude/skills/ ; } \
     | sed -n 's#\(\.claude/skills/[^/]*/[^/]*\)/.*#\1/SKILL.md#p' \
     | sort -u
   ```
   A change to a skill's `references/` or `scripts/` counts — it maps back to that skill's SKILL.md.

**Full-scan triggers** (evaluate every skill — Glob `.claude/skills/**/SKILL.md`): first run, no Commit SHA recorded, the user asks for a full audit, or the diff base is unreachable.

If the changed set is empty, note "no skills changed since {last audit}" and skip to Step 4.3's usage check. (Phase 2 always scans everything — a duplicate can span a changed and an unchanged file.)

### Step 4.2: Evaluate Each Changed Skill

**Primary path.** The `workspace-audit-scan` workflow already ran a lightweight `/skill-creator` eval per changed skill (one agent each, concurrent) and returned `skills` (all verdicts) and `flaggedSkills` (warn/fail, worst first). Don't re-evaluate — Step 4.3 acts on them.

**Inline fallback** (workflow skipped): invoke `skill-creator:skill-creator` directly per changed skill — lightweight eval only, no heavy benchmarking, no edits. Check structure against the skill creation guide: frontmatter with name + triggering description, under 500 lines, clear steps, valid file references.

### Step 4.3: Usage Check, Recurring Failures, and Fixes

- **Usage:** check `.claude/logs/learning-log.md` for mentions of each skill. Categorize: **Healthy** / **Stale** (not used in 60+ days — ask: keep, archive, or delete?) / **Broken** (references disconnected tools or missing files) / **Improvable**.
- **Recurring failures:** read the previous `skill-quality-report-*.md`. A skill flagged then and still flagged now means the earlier fix didn't work — mark ⚠️ RECURRING and prioritize actually fixing it.
- **Verify every fix against its threshold.** After a trim, re-check the count; after a reference fix, confirm the target exists. A fix that doesn't clear the threshold stays flagged.

Save to `results/workspace-audit/skill-quality-report-{YYYY-MM-DD}.md` (totals, per-skill results, top improvements needed). Use `AskUserQuestion`:
- **Fix flagged skills now** / **Just log the report** / **Skip this phase**

---

## Phase 5: Workspace Hygiene

**Goal:** Catch broken links, orphaned files, stale context, and missing tool dependencies. Full procedures in `references/phase5-hygiene-checks.md`.

- **5.1 Broken internal links:** Grep markdown links across `.claude/skills/` and `.claude/context/`; verify each target exists.
- **5.2 Orphaned context files:** context files referenced by zero skills, CLAUDE.md, or rules. Present for review — never auto-delete.
- **5.3 Context freshness:** Is `company/company-context.md` still accurate (team size, tools, departments)? Is `profile.md` current? Is the team directory up to date? Ask the user if anything major changed; update if yes.
- **5.4 Missing tool dependencies:** skills referencing MCP tools not in `.mcp.json`/plugins, CLI tools not installed (`which {tool}`), or `scripts/` files that don't exist.
- **5.5 Protected files:** verify `.claude/skills/workspace/contact-olympus/references/olympus-workspace.json` exists and was never modified. **Never delete, move, or edit it** — flag immediately if it's missing.

Append findings to the dated audit report. Use `AskUserQuestion`:
- **Fix broken links now** / **Just log findings** / **Skip this phase**

---

## Log the Audit and Report

1. Write the full dated report to `results/workspace-audit/YYYY-MM-DD-audit.md` (format in `references/audit-log-template.md`).
2. Append a row to `.claude/logs/audit-log.md` with the date, phases run, **Commit SHA** (`git rev-parse --short HEAD` — next run's Phase 4 diffs against it), key findings, dismissed findings, and the next-due date.
3. Add an entry to `.claude/logs/learning-log.md` so the audit shows up in workspace activity.
4. Present a plain-language summary to the user:

> "Here's your workspace health check:
>
> **Instructions file:** {status}
> **Skills:** {X healthy}, {Y need attention}
> **Duplicated content:** {fixed / none found}
> **New capabilities:** {plugins installed, or "you're up to date"}
> **Automation ideas:** {N suggestions, or "nothing new"}
> **Housekeeping:** {links fixed / files flagged / all clean}
>
> {Top recommendation, if any}"

## Audit Frequency

Default is **monthly**. The user can change it anytime: "run audits weekly/monthly/quarterly" or "don't remind me about audits". Store the preference in `.claude/context/company/preferences.md` under `audit_frequency` (`weekly` | `monthly` | `quarterly` | `off`). When `off`, never remind proactively — manual runs still work.

---

## Execution Model: Multi-Agent Workflow

Phases 2 and 4 fan out over large work-lists — every department directory and every changed skill. Both are driven by the bundled, reusable workflow **`workspace-audit-scan`** (`.claude/workflows/workspace-audit-scan.js`) instead of a serial loop. It is **read-only**: it returns structured findings and applies no edits — every approval gate and file write stays in this main loop.

### How to run it

The workflow is **self-computing** — invoke it with no args:

```
Workflow({ name: "workspace-audit-scan" })
```

(If name resolution fails, invoke with `scriptPath: ".claude/workflows/workspace-audit-scan.js"`. Do not rely on `args` to pass work-lists — args delivery was observed to silently fail in some environments, which is why the workflow self-computes. `args: { fullScan: true }` is an optional override for full-audit requests; if it doesn't take effect, fall back to the inline per-skill path.)

What it does on its own:
- **Scout:** one agent lists the department folders under `.claude/skills/` and computes the changed-since-last-audit skill set from the audit-log Commit SHA (full glob on first run / unreachable base).
- **Phase 2 fan-out:** one read-only agent per department → cross-department tally at the 3+-location threshold → `duplicates`.
- **Phase 4 fan-out:** one agent per changed SKILL.md, each running a lightweight `/skill-creator` eval → `skills` + `flaggedSkills`.

### Consume the return value

`{ duplicates, dedupScanned, skills, flaggedSkills }`:
- `duplicates` → write to `phase2-duplicates.md`, then Step 2.2 verification (read the actual blocks before proposing fixes!)
- `skills` + `flaggedSkills` → Step 4.3. They're already evaluated — don't run a second eval pass.

### Orchestration notes

- **Read-only fan-out, sequential gates:** the workflow never edits files, installs plugins, or asks questions. All `AskUserQuestion` gates run in this main loop AFTER it returns.
- **Error handling:** per-item failures are non-blocking — a timed-out eval or errored department batch is logged and skipped, never aborting the run.
- **Resume:** if killed mid-run, relaunch with the returned `runId` via `resumeFromRunId` — completed agents return cached results instantly.
- **When to skip:** with 1–2 departments or only a handful of skills, run Phases 2 and 4 inline — orchestration overhead isn't worth it.
- **Opt-in:** running `/audit-workspace` is itself the opt-in to launch this workflow. No separate confirmation needed.

---

## Anti-Patterns

- **Don't delete content without user approval** — always present proposed changes first
- **Don't run all 5 phases if the user only wants one** — ask which phases to run if time is limited
- **Don't flag intentional duplication** — some skills include templates for self-containment; only flag 3+-location drift risk
- **Don't extract template-consistency as if it were drift** — read the actual blocks; if content differs per skill, leave it
- **Don't auto-install plugins or automations** — present recommendations and let the user decide
- **Don't re-raise dismissed findings** — check the audit log first
- **Don't block the user's current task for an audit** — note the reminder and move on
- **Don't skip the audit log** — every run gets logged, even partial runs
- **Don't dump raw scan output into chat** — summarize; intermediate results go to `phase2-duplicates.md`
- **Don't show technical jargon to the user** — plain language, workspace language, always

## Troubleshooting

| Problem | Fix |
|---------|-----|
| No audit-log.md exists | First run — create it from the index format and proceed |
| `claude plugin` commands fail | Claude Code may need updating; skip Phase 3 and log it |
| Marketplace manifest not found | `claude plugin marketplace update`, then re-read |
| Workflow returns 0 agents / no-ops | Re-invoke with `scriptPath`; if it persists, run Phases 2 and 4 inline |
| skill-creator can't evaluate a skill | Flag it "needs manual review" and move on |
| `/claude-automation-recommender` unavailable | `claude plugin install claude-code-setup`, reload; if still failing, skip Step 3.4 and log it |
| User dismissed all findings | Log it; don't re-raise next audit unless something changed |
| Subagent fails or times out | Log which batch failed, re-run just that batch |

## References

- `.claude/workflows/workspace-audit-scan.js` — the bundled multi-agent workflow powering Phases 2 and 4 (findings only, no edits)
- `references/audit-log-template.md` — dated report and index formats
- `references/phase5-hygiene-checks.md` — detailed Phase 5 procedures
