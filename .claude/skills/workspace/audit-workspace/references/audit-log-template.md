# Audit Log Template

## Dated Report Format

Each audit run produces a dated report at `results/workspace-audit/YYYY-MM-DD-audit.md`:

```markdown
# Workspace Audit — {YYYY-MM-DD}

**Phases completed:** 1, 2, 3, 4, 5

## Phase 1: CLAUDE.md Optimization
- Quality score: {N}
- Changes: {summary of trims/updates, or "None needed"}

## Phase 2: Duplicate Detection
- Duplicates found: {N} (template-consistency, left alone: {N})
- Duplicates fixed: {N}
- Remaining: {N} (deferred)

## Phase 3: Automation & Plugin Adoption
- New plugins installed: {list or "None"}
- Plugin-vs-skill overlap resolved: {list or "None"}
- Automation recommendations: {list or "None"}
- Flagged for user / declined: {list or "None"}

## Phase 4: Skill Evaluation
- Skills evaluated: {N} (changed since last audit) of {total}
- Passing: {N} | Warn: {N} | Fail: {N} | Recurring: {N}
- Healthy: {N} | Stale: {N} | Broken: {N} | Improvable: {N}
- Skills improved: {list or "None"}

## Phase 5: Workspace Hygiene
- Broken links found: {N} (fixed: {N})
- Orphaned context files: {N} (reviewed: {N})
- Context files updated: {list or "None needed"}
- Missing tool dependencies: {list or "None"}
- Protected files: {OK / FLAGGED}
```

## Index Format

The index lives at `.claude/logs/audit-log.md` — a lightweight file that links to all dated reports. This is the file CLAUDE.md's proactive reminder checks, so it must always reflect the latest run:

```markdown
# Workspace Audit Log

| Date | Report | Phases | Commit | Key Findings |
|------|--------|--------|--------|--------------|
| {YYYY-MM-DD} | [Full report](../../results/workspace-audit/YYYY-MM-DD-audit.md) | 1,2,3,4,5 | {short SHA} | {one-line summary} |

**Dismissed findings (do not re-raise):**
- {YYYY-MM-DD}: {finding the user declined or dismissed}

**Next audit due:** {YYYY-MM-DD}
```

The **Commit** column records `git rev-parse --short HEAD` at the time of the run. The next run's Phase 4 diffs against the most recent row's SHA to evaluate only skills changed since then (see SKILL.md Step 4.1).

## Instructions

- Create `results/workspace-audit/` if it doesn't exist
- Write the full dated report first, then append a row to the index
- If the index doesn't exist, create it with the header row
- Record the Commit SHA so the next run can scope Phase 4 incrementally; if the workspace isn't a git repo yet, write `n/a` (next run full-scans)
- Log every dismissal under "Dismissed findings" — future audits must not re-raise them
- Never delete old rows from the index — it's an append-only log
- Update "Next audit due" from the user's `audit_frequency` preference (default: monthly)
