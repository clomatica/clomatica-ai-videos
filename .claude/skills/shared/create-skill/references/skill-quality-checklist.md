# Skill Quality Checklist

Use this checklist when creating new skills (`/create-skill`) or reviewing existing ones during quarterly maintenance.

---

## Structure & Naming

| Check | Requirement |
|-------|-------------|
| Folder location | `.claude/skills/{department}/{skill-name}/` (2-level nesting only) |
| Folder name | kebab-case, matches `name` field in frontmatter |
| File name | Exactly `SKILL.md` (case-sensitive) |
| File size | Under 5,000 words — move detailed content to `references/` |

## YAML Frontmatter

| Check | Requirement |
|-------|-------------|
| Delimiters | Opening and closing `---` |
| `name` | kebab-case, no spaces/capitals, no "claude"/"anthropic" prefix |
| `description` | Includes: WHAT + WHEN (trigger phrases) + "Do NOT use for..." (negative triggers) |
| `description` length | Under 1,024 characters |
| No XML | No angle brackets (`<` or `>`) in any frontmatter value |
| `metadata.last-updated` | Set to current `YYYY-MM` |
| `metadata.department` | Matches the folder department |
| `metadata.maintainer` | Team or person responsible |

## Required Sections (in order)

| # | Section | Purpose |
|---|---------|---------|
| 1 | `# Skill Name` | Brief description of what the skill does |
| 2 | `## When to Use` | Trigger conditions and proactive suggestions |
| 3 | `## Workflow` / `## Steps` | Numbered steps with clear, actionable instructions |
| 4 | `## Output` | What the skill produces, where it saves |
| 5 | `## Example Interactions` | 1-3 concrete user-Claude interaction examples |
| 6 | `## Context Files` | List of `.claude/context/` files to read |

## Recommended Sections

| # | Section | Purpose |
|---|---------|---------|
| 7 | `## Prerequisites` | Tools, env vars, or files needed before running |
| 8 | `## Anti-Patterns` | What NOT to do (common mistakes) |
| 9 | `## Troubleshooting` | Table with Problem / Cause / Fix columns |
| 10 | `## Self-Improvement` | Instructions to update the skill when edge cases are found |
| 11 | `## Related Skills` | Table of complementary skills |

## Quality Checks

| Check | Why It Matters |
|-------|---------------|
| Instructions are specific and actionable | "Validate the data" is bad; "Run `python validate.py --input {file}`" is good |
| All user questions use `AskUserQuestion` | Never list open-ended numbered questions |
| Negative triggers disambiguate from similar skills | Prevents cross-triggering with related skills |
| Output saves to `results/{subdirectory}/` | Consistent output location across all skills |
| Skill name doesn't duplicate an existing skill | Check CLAUDE.md Skills by Department table |
| Error handling included per step | What can go wrong + how to fix it |
| Examples show realistic input/output | Not just "User says X, Claude does Y" but concrete data |

## Quarterly Review Process

When reviewing skills during quarterly maintenance:

1. Run `last-updated` audit: `grep -r "last-updated" .claude/skills/ --include="SKILL.md"` — flag anything >3 months old
2. Check each skill against this checklist
3. Verify context file references still exist
4. Test trigger phrases: ask Claude "When would you use /skill-name?" — verify description is clear
5. Check for new confusion pairs that need negative triggers
