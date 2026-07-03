export const meta = {
  name: 'workspace-audit-scan',
  description: 'Read-only parallel scan for /audit-workspace: Phase 2 cross-department duplicate detection + Phase 4 per-skill quality evaluation. Fans out one agent per department folder and one agent (running /skill-creator) per changed SKILL.md, then returns structured findings. Applies NO edits and asks NO questions — the /audit-workspace main loop owns every approval gate and file write.',
  phases: [
    { title: 'Scout', detail: 'discover department folders + the changed-since-last-audit skill set' },
    { title: 'Dedup scan', detail: 'one read-only agent per department folder (Phase 2)' },
    { title: 'Skill eval', detail: 'one agent runs /skill-creator per changed SKILL.md (Phase 4)' },
  ],
}

// ---------------------------------------------------------------------------
// Inputs — SELF-COMPUTED by default; `args` is an OPTIONAL override.
//
// Passing work-lists via `args` was observed to silently NOT deliver in some
// environments — the script's `args` global arrived empty and the workflow
// no-oped with 0 agents. So this workflow computes everything itself via a
// scout agent and only uses `args` when explicitly provided:
//
//   args.departments : [{ key, dir }]  — optional override of the department list.
//   args.skills      : [string]        — optional override of the changed-skills set.
//   args.fullScan    : boolean         — optional; force eval of ALL skills.
//
// Unlike a fixed-team workspace, client workspaces have DYNAMIC departments —
// whatever folders exist under .claude/skills/ — so the scout discovers them.
// ---------------------------------------------------------------------------
const SCOUT_SCHEMA = {
  type: 'object',
  additionalProperties: false,
  properties: {
    departments: {
      type: 'array',
      items: {
        type: 'object',
        additionalProperties: false,
        properties: {
          key: { type: 'string', description: 'department folder name, e.g. "marketing"' },
          dir: { type: 'string', description: 'workspace-relative dir, e.g. ".claude/skills/marketing/"' },
        },
        required: ['key', 'dir'],
      },
    },
    base: { type: 'string', description: 'the diff-base SHA used, or "full-scan"' },
    skills: { type: 'array', items: { type: 'string' }, description: 'SKILL.md paths to evaluate' },
  },
  required: ['departments', 'base', 'skills'],
}

const fullScan = !!(args && args.fullScan)
const hasDeptOverride = !!(args && Array.isArray(args.departments) && args.departments.length)
const hasSkillsOverride = !!(args && Array.isArray(args.skills))

let departments = hasDeptOverride ? args.departments : null
let skills = hasSkillsOverride ? args.skills : null

if (departments === null || skills === null) {
  phase('Scout')
  const scouted = await agent(
    `You are scouting a client workspace (current working directory is the workspace root) for the workspace audit. Produce two lists and return them.

1. DEPARTMENTS — list every department folder directly under .claude/skills/ (run: ls -d .claude/skills/*/). Each entry: key = the folder name, dir = the workspace-relative path ending in "/". Include every folder (workspace, shared, and any company department).

2. SKILLS — the set of SKILL.md files to evaluate.
${fullScan ? 'FULL SCAN requested — return EVERY skill: ls .claude/skills/*/*/SKILL.md' : `Incremental rule:
   a. Read .claude/logs/audit-log.md and find the MOST RECENT audit entry's Commit SHA. Call it BASE.
   b. If a BASE SHA exists and is reachable, list skills changed since it:
      { git diff --name-only "$BASE" -- .claude/skills/ ; git ls-files --others --exclude-standard .claude/skills/ ; } | sed -n 's#\\(\\.claude/skills/[^/]*/[^/]*\\)/.*#\\1/SKILL.md#p' | sort -u
   c. If NO base SHA is recorded, BASE is unreachable (history rewritten), or the workspace is not a git repo, FALL BACK to a full scan: ls .claude/skills/*/*/SKILL.md`}

Return departments, base = the SHA you used (or "full-scan"), and skills = the sorted, de-duplicated list of workspace-relative SKILL.md paths (e.g. ".claude/skills/marketing/generate-social-post/SKILL.md"). Return only paths that exist on disk.`,
    { label: 'scout:workspace', phase: 'Scout', agentType: 'general-purpose', schema: SCOUT_SCHEMA }
  )
  if (departments === null) departments = (scouted && scouted.departments) || []
  if (skills === null) skills = (scouted && scouted.skills) || []
  log(`Scout: ${departments.length} departments, ${skills.length} skills to evaluate (base ${scouted ? scouted.base : 'unknown'})`)
}

// Phase 2 — each agent returns one fingerprint PER occurrence (per file:line). The
// orchestrator tallies across departments so a block in 3+ locations = drift risk.
const DEDUP_SCHEMA = {
  type: 'object',
  additionalProperties: false,
  properties: {
    fingerprints: {
      type: 'array',
      items: {
        type: 'object',
        additionalProperties: false,
        properties: {
          key: {
            type: 'string',
            description:
              'Stable normalized id for the duplicated block. The SAME logical content MUST yield the SAME key across files (lowercase, whitespace-collapsed). e.g. for SQL: main table(s)+selected columns; for workflow steps: shared-skill name + first instruction line; for context-embed: a short label like "team-directory-roster".',
          },
          category: { type: 'string', enum: ['sql', 'workflow-instructions', 'context-embed'] },
          location: { type: 'string', description: 'file path:line of THIS occurrence' },
          sample: { type: 'string', description: 'first ~120 chars of the duplicated block' },
        },
        required: ['key', 'category', 'location', 'sample'],
      },
    },
  },
  required: ['fingerprints'],
}

// Phase 4 — lightweight /skill-creator eval per changed skill, run in parallel.
const SKILL_SCHEMA = {
  type: 'object',
  additionalProperties: false,
  properties: {
    path: { type: 'string' },
    status: { type: 'string', enum: ['pass', 'warn', 'fail'] },
    score: { type: 'number', description: '0-100 quality score' },
    wordCount: { type: 'number' },
    issues: { type: 'array', items: { type: 'string' } },
  },
  required: ['path', 'status', 'score', 'issues'],
}

// === Phase 2: cross-department duplicate detection ===
// Barrier (parallel) is correct here: the 3+-location threshold is a CROSS-batch
// tally — the same block in two departments only counts once we have every
// department's fingerprints together.
phase('Dedup scan')
const dedupBatches = (await parallel(
  departments.map((d) => () =>
    agent(
      `You are scanning the client-workspace skill directory "${d.dir}" for DUPLICATED content that creates drift risk. Read only the *.md files under that directory.

Find three categories of duplication and emit one fingerprint per occurrence (per file:line):
  (A) sql — database queries (SELECT ... FROM ...). key = main table name(s) + selected columns/aggregates, normalized (lowercase, whitespace-collapsed) so the same query in two files yields the SAME key.
  (B) workflow-instructions — copy-pasted multi-step instructions (5+ consecutive identical lines), e.g. blocks referencing shared workspace skills (save-changes, connect-tool, create-skill). key = referenced-skill name + the first instruction line.
  (C) context-embed — blocks of 5+ lines replicating content from .claude/context/ (company profile, company-context, preferences) or .claude/shared-references/ (team directory). key = a short label for the embedded block.

Rules: report only EXACT or NEAR-verbatim duplicates of 5+ consecutive lines — the lines must be substantially the same TEXT, not just the same structure. Do NOT report mere semantic similarity, and do NOT fingerprint a block whose lines share only a heading/skeleton (e.g. a Self-Improvement footer, an Anti-Patterns template, a steps skeleton) while the actual content differs per skill — that is template-consistency, not drift. When in doubt, compare the literal words: if a reader couldn't copy block A verbatim into B's file, it is NOT a duplicate. Emit every genuine occurrence as its own fingerprint even when it appears only once in your directory — the orchestrator does the cross-department tally.`,
      { label: `dedup:${d.key}`, phase: 'Dedup scan', agentType: 'Explore', schema: DEDUP_SCHEMA }
    )
  )
)).filter(Boolean)

// Tally fingerprints across ALL departments. A key in 3+ distinct locations is the
// documented drift threshold (2 = reasonable cross-reference, 3+ = risk).
const byKey = {}
for (const batch of dedupBatches) {
  for (const fp of batch.fingerprints || []) {
    if (!byKey[fp.key]) byKey[fp.key] = { key: fp.key, category: fp.category, sample: fp.sample, locations: [] }
    if (!byKey[fp.key].locations.includes(fp.location)) byKey[fp.key].locations.push(fp.location)
  }
}
const duplicates = Object.values(byKey)
  .filter((g) => g.locations.length >= 3)
  .sort((a, b) => b.locations.length - a.locations.length)
log(`Dedup scan: ${Object.keys(byKey).length} distinct blocks across ${dedupBatches.length} departments, ${duplicates.length} duplicated in 3+ locations`)

// === Phase 4: per-skill /skill-creator eval ===
// Independent per skill, so no barrier needed beyond parallel()'s concurrency cap;
// a failed eval drops to null. agentType 'general-purpose' is required so each
// agent has the Skill tool and can invoke the skill-creator plugin.
phase('Skill eval')
const skillResults = (await parallel(
  skills.map((p) => () =>
    agent(
      `Evaluate the quality of the workspace skill at ${p} by invoking the \`skill-creator:skill-creator\` plugin skill via the Skill tool.

Steps:
1. Invoke \`skill-creator:skill-creator\` and ask it to run a lightweight quality eval of the single skill at ${p}. Keep it minimal and fast — do NOT request heavy multi-iteration variance benchmarking, and do NOT edit any files.
2. Read the full SKILL.md yourself to confirm word count and frontmatter.

From skill-creator's assessment plus your read, produce the structured result for path = ${p}:
  - score: 0-100 quality score (skill-creator's, or your synthesis of its verdict).
  - status: pass (>=80), warn (60-79), fail (<60).
  - wordCount: word count of the SKILL.md body.
  - issues: concrete, actionable issues — frontmatter gaps, weak/ambiguous description triggers, missing "do NOT use" boundary, over 500 lines, missing output location, stale references to skills/context files/tools that no longer exist, structure problems.

If the skill-creator skill is unavailable to you, fall back to scoring the SKILL.md directly against those same criteria and add the issue "skill-creator unavailable — heuristic eval used".`,
      { label: `eval:${p.split('/').slice(-2)[0]}`, phase: 'Skill eval', agentType: 'general-purpose', schema: SKILL_SCHEMA }
    )
  )
)).filter(Boolean)

const flagged = skillResults.filter((s) => s.status !== 'pass').sort((a, b) => a.score - b.score)
log(`Skill eval: ${skillResults.length} evaluated, ${flagged.length} flagged (warn/fail)`)

// Findings only — the main loop presents these through AskUserQuestion and owns every edit.
return {
  duplicates, // [{ key, category, sample, locations[] }] appearing in 3+ locations
  dedupScanned: Object.keys(byKey).length,
  skills: skillResults, // full per-skill scores
  flaggedSkills: flagged, // warn/fail subset, worst score first — present these for fixes (already eval'd)
}
