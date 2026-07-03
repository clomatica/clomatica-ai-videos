# Skill Creation Guide — Detailed Reference

This reference file contains detailed patterns, examples, and testing guidance from Anthropic's official "Complete Guide to Building Skills for Claude". Read this when creating or reviewing skills.

## Skill Use Case Categories

### Category 1: Document & Asset Creation
**Used for:** Creating consistent, high-quality output including documents, presentations, apps, designs, code, etc.

**Key techniques:**
- Embedded style guides and brand standards
- Template structures for consistent output
- Quality checklists before finalizing
- No external tools required — uses Claude's built-in capabilities

### Category 2: Workflow Automation
**Used for:** Multi-step processes that benefit from consistent methodology, including coordination across multiple MCP servers.

**Key techniques:**
- Step-by-step workflow with validation gates
- Templates for common structures
- Built-in review and improvement suggestions
- Iterative refinement loops

### Category 3: MCP Enhancement
**Used for:** Workflow guidance to enhance the tool access an MCP server provides.

**Key techniques:**
- Coordinates multiple MCP calls in sequence
- Embeds domain expertise
- Provides context users would otherwise need to specify
- Error handling for common MCP issues

---

## Workflow-Aware Skills (Parallel Execution)

Many skills repeat the same independent operation over a **fixed, known work-list** — clients (gather feedback, health checks), repos (sync/audit sweeps), prospects or companies (research), channels, doc sections, or schedules. Others **gather from multiple independent sources** that could run at once (database + CRM + Slack + docs). These are exactly the skills that benefit from the **Workflow tool** (`pipeline()` / `parallel()`) instead of a serial loop: independent units run concurrently, then results fan back in for aggregation.

**When a skill qualifies, give it a `## Parallel Execution (Workflow)` section** (right after the main steps). Document five things:

1. **Shape** — the concrete fan-out pipeline using the skill's *real* step names, e.g. `list clients → fan-out per client: [fetch data → score → draft] → gather → summary`.
2. **Work-list** — exactly how to build the list inline *before* fanning out (the API call, the discovery query, the source list). Scout inline first, then pass the list to the workflow.
3. **Concurrency & batching** — wave size tuned to each API/MCP's rate limits; note the ~16 concurrent cap.
4. **Error handling** — which per-item failures must be non-blocking (`.filter(Boolean)`), e.g. one unreachable source should not abort the run.
5. **Sequential gates** — any human-confirm / approval step, and especially **production data writes**, must stay sequential and run *after* the fan-out.

**Common reusable shapes:**
- **Fan-out-over-clients** (gather → score → draft)
- **Multi-repo or multi-source sync/audit sweep**
- **Fan-out-over-prospects** (research → enrich → CRM-write)
- **Doc-gap sync** (per-section fetch+compare → aggregate → parallel write)
- **Task-queue executor**

**Don't add the section** for interactive / human-in-the-loop, single-unit, or single-action skills (validate a title, make a PDF, post one message, one SQL query) — orchestration overhead isn't worth it.

---

## Description Writing Guide

### Formula
```
[What it does] + [When to use it (trigger phrases)] + [Key capabilities or scope limits]
```

### Good Examples
```yaml
# Specific and actionable
description: Analyzes production database issues and traces records through the attribution pipeline. Use when user says "investigate data", "trace a record", "find missing payouts", "debug attribution".

# Includes negative triggers to avoid confusion with similar skills
description: Build SQL queries against the production database with proper joins and filters. Use when user says "build a query", "write SQL", "query the DB". Do NOT use for executing queries (use query-postgres instead).

# Clear value proposition with file types
description: End-to-end customer onboarding workflow. Handles program design creation, launch roadmap, and Notion page setup. Use when user says "onboard new client", "set up a new project", "client workflow". Produces .md files and Notion pages.

# Scoped to specific domain
description: Create and manage DynamoDB schedules for token balance fetching, subgraph data, and other provider types. Use specifically for schedule creation, not for general DynamoDB operations.
```

### Bad Examples
```yaml
# Too vague — won't trigger on anything specific
description: Helps with projects.

# Missing triggers — Claude doesn't know WHEN to load it
description: Creates sophisticated multi-page documentation systems.

# Too technical, no user-facing triggers
description: Implements the Project entity model with hierarchical relationships.

# Too broad — will over-trigger
description: Processes documents.
```

---

## Workflow Patterns

### Pattern 1: Sequential Workflow Orchestration
**Use when:** Your users need multi-step processes in a specific order.

```markdown
## Workflow

### Step 1: Gather Requirements
Call MCP tool: `notion-search`
Parameters: project name, client info

### Step 2: Create Program Design
Use template from `references/program-design-template.md`
Wait for: user approval of design

### Step 3: Set Up in Notion
Call MCP tool: `notion-create-page`
Parameters: title, parent_page, content (from Step 2)

### Step 4: Notify Team
Call MCP tool: `slack_post_message`
Template: welcome_message_template
```

**Key techniques:** Explicit step ordering, dependencies between steps, validation at each stage, rollback instructions for failures.

### Pattern 2: Multi-MCP Coordination
**Use when:** Workflows span multiple services.

```markdown
### Phase 1: Data Collection (Linear MCP)
1. Fetch project issues
2. Categorize by status
3. Generate summary

### Phase 2: Report Creation (Local)
1. Apply report template
2. Format data
3. Save to results/

### Phase 3: Distribution (Slack plugin)
1. Post summary to #team-updates
2. Include links and task references
```

**Key techniques:** Clear phase separation, data passing between MCPs, validation before moving to next phase, centralized error handling.

### Pattern 3: Iterative Refinement
**Use when:** Output quality improves with iteration.

```markdown
### Initial Draft
1. Fetch data via MCP
2. Generate first draft
3. Save to temporary file

### Quality Check
1. Run validation against checklist
2. Identify issues:
   - Missing sections
   - Inconsistent formatting
   - Data validation errors

### Refinement Loop
1. Address each identified issue
2. Regenerate affected sections
3. Re-validate
4. Repeat until quality threshold met

### Finalization
1. Apply final formatting
2. Generate summary
3. Save final version
```

**Key techniques:** Explicit quality criteria, iterative improvement, validation scripts, know when to stop iterating.

### Pattern 4: Context-Aware Tool Selection
**Use when:** Same outcome, different tools depending on context.

```markdown
### Decision Tree
1. Check file type and size
2. Determine best storage location:
   - Large files (>10MB): Use cloud storage MCP
   - Collaborative docs: Use Notion/Docs MCP
   - Code files: Use GitHub MCP
   - Temporary files: Use local storage

### Execute Storage
Based on decision:
- Call appropriate MCP tool
- Apply service-specific metadata
- Generate access link

### Provide Context to User
Explain why that storage was chosen
```

**Key techniques:** Clear decision criteria, fallback options, transparency about choices.

### Pattern 5: Domain-Specific Intelligence
**Use when:** Your skill adds specialized knowledge beyond tool access.

The skill embeds business rules, compliance requirements, or domain expertise that users would otherwise need to specify manually. For example, a skill that knows your attribution pipeline and can diagnose issues without the user explaining how the pipeline works.

**Key techniques:** Domain expertise embedded in logic, compliance/validation before action, comprehensive documentation, clear governance.

---

## Script Ownership Patterns

Skills that include executable scripts (bash, python, etc.) must follow these rules:

### Scripts Live Inside the Skill

All scripts belong in `{skill}/scripts/`. Never create a root-level `scripts/` directory or any shared scripts directory outside of skills. Each skill owns its scripts locally.

### One Script, One Owner

When the same script could be used by multiple skills, **one skill owns it** and the others reference that skill. For example:
- `run_query.sh` lives in `/query-postgres` → other skills say "run the query via `/query-postgres`"
- `query_dynamodb.sh` lives in `/query-dynamodb` → other skills say "use `/query-dynamodb` to check schedules"
- `validate_csv.sh` lives in `/upload-to-s3-scripts-bucket` → other skills say "validate via `/upload-to-s3-scripts-bucket`"

The owning skill is whichever skill provides the **primary capability** the script delivers.

### Delegating Skills Replace Bash Blocks with Prose

When a skill delegates to another skill (instead of calling the script directly), replace bash code blocks with prose instructions:

```markdown
# Bad — calling another skill's script directly
Run `.claude/skills/engineering/query-postgres/scripts/run_query.sh production "SELECT ..."`

# Good — delegating to the owning skill
Run the following query via `/query-postgres` against the production database:
```sql
SELECT ...
```
```

### Path Resolution in Scripts

Scripts nested inside skill folders that need to find the workspace root (e.g., to source `.env`) should use `git rev-parse --show-toplevel` instead of relative path navigation:

```bash
# Bad — breaks when script is moved
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_DIR="$(dirname "$(dirname "$(dirname "$SCRIPT_DIR")")")"

# Good — works from any depth
WORKSPACE_DIR="$(git rev-parse --show-toplevel 2>/dev/null)" || { echo "Not inside a git repository"; exit 1; }
```

### Validation Checklist for Scripts

- [ ] Script lives in `{skill}/scripts/`, not in a root-level directory
- [ ] If multiple skills need this functionality, only one skill owns the script
- [ ] Other skills reference the owning skill by name, not the script path
- [ ] Scripts that need `.env` use `git rev-parse --show-toplevel` for path resolution
- [ ] SKILL.md references the script with the correct relative path (e.g., `.claude/skills/engineering/query-postgres/scripts/run_query.sh`)

---

## Database Query Patterns

Skills that interact with the production database must follow these rules:

### SQL Queries Go in `references/`

Never put SQL queries inline in SKILL.md. Store them in a `references/` file (e.g., `references/queries.md`) and reference them from the workflow steps. This follows the progressive disclosure model and keeps SKILL.md concise.

### SELECT Queries: Delegate to `/query-postgres`

When a skill needs to run a read-only query, it should say "Run the query via `/query-postgres`" — never instruct Claude to call `psql` or `run_query.sh` directly. `/query-postgres` handles connection boilerplate, `.env` loading, user approval, and safety checks.

### Write Queries: Admin Required

Skills must **never** execute UPDATE, DELETE, or INSERT queries. `/query-postgres` and `run_query.sh` are SELECT-only and will reject write statements. When a skill produces a write query:

1. Mark it clearly with: `> **Admin required** — This is a write query. Present the filled-in query to the user and tell them an admin must run it on the production database.`
2. The skill's workflow step should say "present the query to the user" — not "run the query"
3. The Related Skills table should clarify that `/query-postgres` is used for SELECT queries only

### Example Reference File Structure

```
references/queries.md:

## Discovery Query (SELECT)
Run via `/query-postgres` against the production database.
[SQL here]

## Fix Query (UPDATE)
**Admin required** — present to user, admin must run on production.
[SQL here]
```

---

## Testing Approach

### 1. Triggering Tests
**Goal:** Ensure your skill loads at the right times.

Create a mental test suite:

```
Should trigger:
- "Help me [exact use case 1]"
- "I need to [paraphrased use case]"
- "[Domain keyword] for [specific context]"

Should NOT trigger:
- "What's the weather in San Francisco?"
- Unrelated tasks from other departments
- Similar but different tasks (that should use a different skill)
```

### 2. Functional Tests
**Goal:** Verify the skill produces correct outputs.

Test cases:
- Valid outputs generated for typical input
- MCP/API calls succeed (if applicable)
- Error handling works when things fail
- Edge cases covered (empty input, missing data, etc.)

### 3. Performance Comparison
**Goal:** Prove the skill improves results vs. baseline.

Compare:
```
Without skill:
- User provides instructions each time
- Multiple back-and-forth messages
- Inconsistent results
- More token consumption

With skill:
- Automatic workflow execution
- 1-2 clarifying questions only
- Consistent output format
- Less token consumption
```

---

## Iteration Signals

### Under-triggering (skill doesn't load when it should)
**Signs:**
- Users manually typing `/skill-name` instead of it auto-loading
- Users asking "when should I use this?"
- Skill doesn't load for paraphrased requests

**Fix:** Add more detail and nuance to the description — include keywords, particularly for technical terms.

### Over-triggering (skill loads when it shouldn't)
**Signs:**
- Skill loads for irrelevant queries
- Users confused about why it activated
- Conflicts with other skills

**Fix:** Add negative triggers ("Do NOT use for..."), be more specific about scope, clarify domain.

### Execution Issues
**Signs:**
- Inconsistent results across runs
- MCP/API call failures
- User needing to correct Claude mid-workflow

**Fix:** Improve instructions specificity, add error handling, add explicit validation steps.

---

## Writing Instructions — Advanced Tips

### Avoid Ambiguity
```markdown
# Bad
Make sure to validate things properly

# Good
CRITICAL: Before calling create_project, verify:
- Project name is non-empty
- At least one team member assigned
- Start date is not in the past
```

### Combat Model Laziness
Add explicit encouragement for thoroughness — this is more effective in the SKILL.md body than in user prompts:
```markdown
## Performance Notes
- Take your time to do this thoroughly
- Quality is more important than speed
- Do not skip validation steps
```

### Use Progressive Disclosure for Large Skills
If your skill needs extensive reference material:
1. Keep SKILL.md focused on the core workflow (under 5,000 words)
2. Move templates to `references/template-name.md`
3. Move API docs to `references/api-guide.md`
4. Link clearly: "Before writing queries, consult `references/api-patterns.md` for rate limiting guidance, pagination patterns, and error codes"

---

## Full Validation Checklist

### Before You Start
- [ ] Identified 2-3 concrete use cases
- [ ] Tools identified (built-in or MCP)
- [ ] Planned folder structure
- [ ] Checked no duplicate skill exists

### During Development
- [ ] Folder named in kebab-case
- [ ] SKILL.md file exists (exact spelling)
- [ ] YAML frontmatter has `---` delimiters
- [ ] `name` field: kebab-case, no spaces, no capitals
- [ ] `description` includes WHAT and WHEN (trigger phrases)
- [ ] `description` under 1024 characters
- [ ] No XML tags (`<` or `>`) anywhere
- [ ] No "claude" or "anthropic" in skill name
- [ ] Instructions are clear and actionable
- [ ] Error handling included
- [ ] Examples provided
- [ ] References clearly linked
- [ ] Context files listed
- [ ] SKILL.md under 5,000 words

### Database Query Checks (if skill uses SQL)
- [ ] SQL queries stored in `references/` files, not inline in SKILL.md
- [ ] SELECT queries delegate to `/query-postgres`
- [ ] Write queries (UPDATE, DELETE, INSERT) marked with "Admin required" note
- [ ] Related Skills table clarifies `/query-postgres` is SELECT-only

### Script Checks (if skill uses scripts)
- [ ] Scripts live in `{skill}/scripts/`, not in a root-level directory
- [ ] If multiple skills need the same functionality, only one skill owns the script
- [ ] Other skills reference the owning skill by name, not the script path
- [ ] Scripts that need `.env` use `git rev-parse --show-toplevel` for path resolution

### Before Merging
- [ ] Tested triggering on obvious tasks
- [ ] Tested triggering on paraphrased requests
- [ ] Verified doesn't trigger on unrelated topics
- [ ] Functional tests pass (workflow completes)
- [ ] CLAUDE.md updated with new skill entry

### After Deployment
- [ ] Test in real conversations
- [ ] Monitor for under/over-triggering
- [ ] Collect user feedback
- [ ] Iterate on description and instructions
- [ ] Update `last-updated` in metadata

---

## YAML Frontmatter — Complete Reference

### Required Fields
```yaml
---
name: skill-name-in-kebab-case
description: What it does and when to use it. Include specific trigger phrases.
metadata:
  maintainer: Department Team
  last-updated: YYYY-MM
  department: Department
---
```

### All Optional Fields
```yaml
name: skill-name
description: [required description]
license: MIT                                    # Optional: License for open-source
compatibility: "Requires psql CLI and AWS CLI"  # Optional: Environment requirements (1-500 chars)
allowed-tools: "Bash(python:*) WebFetch"        # Optional: Restrict tool access
metadata:                                       # Optional: Custom fields
  maintainer: Team Name
  last-updated: YYYY-MM
  department: Department
  version: 1.0.0
  mcp-server: server-name                       # If skill depends on an MCP server
  category: productivity
  tags: [project-management, automation]
```

### Security Notes
**Allowed:** Any standard YAML types (strings, numbers, booleans, lists, objects). Custom metadata fields. Long descriptions (up to 1024 characters).

**Forbidden:** XML angle brackets (`<` or `>`). Skills named with "claude" or "anthropic" prefix.

**Why:** Frontmatter appears in Claude's system prompt. Malicious content could inject instructions.
