---
name: save-changes
description: Save workspace changes to GitHub — commits and pushes to the remote repository, and handles the first-time setup automatically (creates a private GitHub repository) if the workspace isn't online yet. Use whenever the user wants to save, back up, or share their work. Trigger phrases include "push changes", "save changes", "commit and push", "push to git", "ship this", "back up my workspace", "upload to github", "subir a github", "guardar cambios". Always use this skill after updating skills or context files — never push manually.
metadata:
  maintainer: All Teams
  last-updated: 2026-07-03
  department: Workspace
---

# Save Changes

Save workspace changes to the remote repository. If the workspace isn't on GitHub yet, this skill sets that up first (one time), then saves.

Never assume the user knows what git, GitHub, or a repository is. Explain in plain words: "GitHub is a safe place online where your workspace gets backed up, so nothing is ever lost and your team can share the same setup."

## When to Use

Use this skill whenever the user has made changes and wants to save them — including the very first time, when the workspace has never been uploaded anywhere.

## Workflow

### Step 0: Check if the workspace is online yet

```bash
git -C . rev-parse --is-inside-work-tree 2>/dev/null
git remote get-url origin 2>/dev/null
```

- If `origin` exists → skip to **Step 1** (everyday saving).
- If there's no git repository at all → `git init -b main`, then continue with **First-Time Setup**.
- If there's a repository but no `origin` → continue with **First-Time Setup**.

## First-Time Setup (only when there's no remote)

This runs once. After it's done, every future save goes straight to Step 1.

### A. Make sure the GitHub tool is installed

```bash
command -v gh
```

If missing, install it (tell the user: "I'm installing the GitHub connector — takes a minute"):

- **Mac:** `brew install gh`
- **Windows:** `winget install --id GitHub.cli`

If the install fails, see Troubleshooting.

### B. Sign in to GitHub

```bash
gh auth status
```

If not signed in:

> "I'll open GitHub in your browser. A code will appear here — type it into the browser page and click Authorize. That's it."

```bash
gh auth login --web --git-protocol https
```

Wait for the user to finish in the browser. Verify with `gh auth status` before continuing.

If the user doesn't have a GitHub account, tell them to create one first at github.com/signup (free), then retry.

### C. Safety check before uploading

Before anything goes online, verify secrets stay local:

1. Confirm `.gitignore` exists and contains `.env` and `.mcp.json`. If either is missing, add it.
2. Run `git status --ignored --short | head -20` and confirm `.env` and `.mcp.json` show as ignored.
3. Run `git log --all --diff-filter=A -- .env .mcp.json` — if either file was EVER committed, STOP and tell the user: "I found credentials in the workspace history. I'll remove them before uploading." Remove them from history (or re-init: delete `.git`, `git init -b main`, fresh initial commit) before proceeding.

Never upload a workspace where secrets are tracked. This check is non-negotiable.

### D. Create the repository and upload

Use the workspace folder name (kebab-case) as the repository name. Confirm with the user first:

> "I'll create a private space on GitHub called `{folder-name}` — only you and people you invite can see it. Good?"

```bash
git add -A && git diff --cached --quiet || git commit -m "Workspace snapshot before first upload"
gh repo create {folder-name} --private --source=. --remote=origin --push
```

If the name is taken, suggest `{folder-name}-workspace` and retry.

Then tell the user:

> "Done — your workspace is backed up at {repository URL}. It's private: only you can see it.
> From now on, whenever you want to save your work, just say **"save changes"**.
> To give a teammate access: open {repository URL}/settings/access and invite them by email."

If there were no other pending changes, you're done. Otherwise continue with Step 1.

## Everyday Saving

### Step 1: Pull Latest Changes

```bash
git pull origin main
```

If there are conflicts:
1. List the conflicting files to the user
2. Ask the user how to resolve each conflict
3. After resolution, stage the resolved files

### Step 2: Review and Commit Changes

1. Run `git status` and `git diff` to review changes
2. **Check for sensitive files** - Ensure no secrets, credentials, or work-specific outputs are being committed
3. Stage changes with `git add <files>`
4. Commit with a clear message:
   - `add <what>` - New functionality
   - `fix <what>` - Bug fixes
   - `update <what>` - Changes to existing functionality
   - `remove <what>` - Removing functionality

### Step 3: Push

**Always ask the user for confirmation before pushing.** Show them the commit message and files changed, and wait for explicit approval.

```bash
git push origin main
```



## Examples

**Example: First save of a brand-new workspace**
- User: "can we back this up somewhere?"
- No `origin` → First-Time Setup: gh not installed → `brew install gh` → browser sign-in → safety check clean → created private repo `renata-workspace` → pushed. Told user to just say "save changes" from now on.

**Example: Everyday save**
- User: "save changes"
- `origin` exists → pulled, reviewed diff, committed `update one-on-one skill with new questions`, showed the user, pushed after approval, notified the team channel.

## Anti-Patterns

- **Don't push without user confirmation** — Always show the commit message and changed files, then wait for explicit approval before pushing
- **Don't commit sensitive files** — Check for `.env`, credentials, output files, and `.mcp.json` before staging
- **Don't skip `git pull` before pushing** — Always pull first to avoid non-fast-forward rejections
- **Don't run First-Time Setup when a remote exists** — If `origin` is already configured, go straight to everyday saving


## Troubleshooting

| Problem | Cause | Fix |
|---------|-------|-----|
| `git push` rejected — "non-fast-forward" | Remote has commits not in local branch | Run `git pull origin main` first and resolve conflicts |
| Merge conflict on `git pull` | Concurrent edits to the same file | List conflicting files, ask user how to resolve each |
| Sensitive files staged accidentally | `.env`, credentials included | Remove from staging with `git reset HEAD <file>`; review `.gitignore` |
| `git push` fails — "'origin' does not appear to be a git repository" | Workspace was never uploaded | Run First-Time Setup (Step 0 detects this automatically) |
| `brew` / `winget` not found | Package manager missing | Mac: install Homebrew first (`/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"`). Windows: download gh from cli.github.com and run the installer. |
| Browser sign-in doesn't open | Headless or blocked browser | Run `gh auth login --web` again and give the user the printed URL + one-time code to open manually |
| `gh repo create` says name already exists | Repo name taken | Append `-workspace` (or the company name) to the repo name and retry |
| Push rejected (large files) | Files over 50MB tracked | Find them with `find . -size +50M -not -path "./.git/*"`, add to `.gitignore`, untrack with `git rm --cached`, commit, retry |
| User has no GitHub account | — | Send them to github.com/signup (free), wait, then retry sign-in |
| Secrets found in history (safety check) | `.env`/`.mcp.json` committed in the past | Do NOT push. Easiest fix: `rm -rf .git && git init -b main && git add -A && git commit -m "Initial workspace setup"` — fresh history with secrets ignored — then create the repo |


## Self-Improvement

After completing this workflow, if you discovered:
- A new type of merge conflict or resolution pattern → update this skill
- A commit message convention that should be standardized → update the Workflow section
- The user's company uses a different code host (GitLab, Bitbucket) → capture a variant and note it in the learning log

Ask the user if they want to save the improvement.
