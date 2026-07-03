# Phase 5: Workspace Hygiene — Detailed Procedures

Detailed check procedures for Phase 5 of the workspace audit.

---

## 5.1: Broken Internal Links

**Goal:** Find markdown links that point to files that don't exist.

**Procedure:**

1. Use Grep with pattern `\[.*\]\([^)]*\.md\)` across `.claude/skills/` and `.claude/context/` (glob `*.md`, output_mode `content`)
2. Extract the link target path from each match
3. Resolve relative paths against the source file's directory
4. For each resolved path, use Glob to verify the file exists
5. Collect broken links into a table: source file, line, link text, target, status

**Notes:**
- Ignore external URLs (http/https) and anchor-only links (`#section`)
- Some links are workspace-root-relative, others file-relative — check both interpretations before flagging as broken

---

## 5.2: Orphaned Context Files

**Goal:** Find context files not referenced by any skill.

**Procedure:**

1. Glob `.claude/context/**/*.md`, excluding directories that are read by convention rather than by explicit link (skip `.claude/logs/` entirely — learning-log and audit-log are append-only logs, never linked by skills)
2. For each remaining context file, Grep for its filename across `.claude/skills/` (glob `*.md`), the root `CLAUDE.md`, and `.claude/rules/` if present
3. Flag files with zero references

**Important:** Do NOT auto-delete orphaned files. They may be newly created, used directly by the user, or referenced by convention. Present them for review with a recommendation: wire into a relevant skill, or archive.

---

## 5.3: Context Freshness

**Goal:** Catch company context that has drifted from reality.

**Procedure:**

1. Read `.claude/context/company/company-context.md` and `.claude/context/company/profile.md`
2. Compare against current workspace state: department folders under `.claude/skills/`, connected tools (`.mcp.json` + installed plugins), and recent activity in `.claude/logs/learning-log.md`
3. Check `.claude/shared-references/team-directory.md` (if present) — ask the user if the roster is current
4. Ask the user in plain language if anything major changed since setup (team size, tools, departments, priorities). If yes, update the context files with their answers.

---

## 5.4: Skill Dependencies on Missing Tools

**Goal:** Ensure skills don't reference tools that aren't available.

### MCP Tools
1. Grep all SKILL.md files for `mcp__` patterns
2. Run `claude mcp list` to see configured servers
3. **Separate noise from real failures.** Plugin-bundled MCP servers often show "Needs authentication" simply because they're unauthenticated — that is NOT a workspace defect unless a skill actually depends on that tool. Only flag a missing dependency when a server a skill actually uses is absent from both `.mcp.json` and the installed plugins. Roll the rest into one informational line.

### CLI Tools
1. Grep all SKILL.md files for CLI tools a skill actually invokes (e.g. `git`, `gh`, `psql`, `uv`)
2. For each, run `which {tool}` to verify it's installed
3. Flag a missing CLI only if an operational skill invokes it — ignore tools that appear solely as examples inside this audit skill's own docs

### Scripts
1. Grep all SKILL.md files for `scripts/` path references
2. Resolve each path relative to the skill's directory and verify the file exists with Glob
3. Flag missing scripts

**If a tool is missing:** never ask the client to install it themselves with terminal commands. Either fix it directly (if safe and automatic) or flag it for `/contact-olympus` so the Olympus team handles it.

---

## 5.5: Protected Files

**Goal:** Verify the workspace's identity files are intact.

**Procedure:**

1. Verify `.claude/skills/workspace/contact-olympus/references/olympus-workspace.json` exists and is valid JSON
2. If missing or corrupted, flag it prominently in the report and tell the user to reach out to Olympus — without it, `/contact-olympus` loses its identity and the Olympus team can't see workspace health
3. **Never** delete, move, regenerate, or "clean up" this file during any audit fix

Other never-touch items during audit cleanups:
- `.claude/logs/learning-log.md` and `.claude/logs/audit-log.md` (append-only history)
- `.mcp.json` (holds the client's credentials — fix entries only when a connection is being repaired on purpose)
