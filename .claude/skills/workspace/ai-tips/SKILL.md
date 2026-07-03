---
name: ai-tips
description: Show practical tips for working effectively with Claude Code — how to ask clearly, when to intervene, how to verify results, and how to build reusable skills from your work. Use when the user says "tips", "how do I use this", "how to work with Claude", "help me get better at this", "best practices", "I'm not sure how to ask", "how to prompt", "ai tips". Do NOT use for tool connection issues or skill creation.
metadata:
  maintainer: All Teams
  last-updated: 2026-07-03
  department: Workspace
---

# AI Tips

Practical tips for getting the most out of your Clomatica workspace. No jargon, no theory — just what works.

## When to Use

- The user asks how to work with Claude effectively
- The user seems unsure how to phrase a request
- The user is new and exploring
- The user gets a result they didn't expect and wants to improve next time

When triggered, show the 3-5 tips most relevant to what the user is doing. Do not dump all tips at once.

## Tips

### 1. Be Specific About What You Want

The clearer your request, the better the result.

| Instead of... | Try... |
|---------------|--------|
| "Write something about our product" | "Write a 3-paragraph summary of our Q1 results, focusing on customer growth" |
| "Help me with this data" | "Compare last month's sales to the same month last year and tell me what changed" |
| "Make a report" | "Create a weekly sales report with total revenue, top 5 clients, and deals closing this week" |

**Why it matters:** Claude works best when it knows the format, the audience, and the goal.

### 2. Include Context That Matters

Claude can only work with what you give it. If something is important, say it.

- **Who is this for?** "This email is for a client who is unhappy about a delay"
- **What tone?** "Keep it friendly but professional"
- **What constraints?** "Keep it under 200 words" or "Use only data from March"
- **What do you already know?** "The client already knows about the price change, so focus on the new timeline"

### 3. Break Big Tasks Into Steps

If a task has multiple parts, tell Claude to do them one at a time.

- "First, pull last week's numbers. Then compare them to the target. Then write a summary of where we're behind."
- "Start by listing all open deals. I'll tell you which ones to focus on."

**Why it matters:** Smaller steps give you a chance to check each part before moving on. You stay in control without doing the work yourself.

### 4. Tell Claude When Something Is Wrong

If a result isn't right, say what's wrong — don't just ask again.

| Instead of... | Try... |
|---------------|--------|
| "Try again" | "The tone is too formal. Make it more conversational." |
| "That's not what I wanted" | "I wanted the summary grouped by region, not by product" |
| "Do it better" | "Add specific numbers and remove the bullet points" |

Claude learns from your corrections within the conversation. The more specific your feedback, the better the next attempt.

### 5. Know When to Let Claude Work vs. When to Step In

**Let Claude work when:**
- The task is clear and well-defined
- You've given enough context
- It's a routine task (reports, summaries, drafts, data lookups)

**Step in when:**
- You see it going in the wrong direction early — correct sooner rather than later
- The task needs a judgment call only you can make
- You want to add information Claude doesn't have

**You don't need to watch every step.** If you asked for a report, let it finish. Review the result, then give feedback.

### 6. Verify Important Results

For anything that goes to a client, a boss, or gets acted on:

- **Check the numbers.** If Claude pulled data, spot-check a few figures against the source.
- **Check the tone.** Read it as if you were receiving it. Does it sound like Clomatica?
- **Check the facts.** Claude can make confident-sounding mistakes. If something sounds surprising, verify it.

### 7. Turn Repeated Work Into Skills

This is where your workspace becomes truly valuable.

**When you notice yourself asking for the same kind of thing more than twice** — a weekly report, a client follow-up template, a data check — that's a skill waiting to happen.

Just say: "Let's turn this into a skill I can reuse."

Claude will capture the exact steps, format, and logic into a reusable command. Next time, you just run the command and it's done.

**Examples of things that become great skills:**
- "Every Monday I need a summary of..." → becomes a one-command weekly report
- "When a new client signs up, I always need to..." → becomes an onboarding checklist
- "Check if our inventory levels are..." → becomes an inventory alert

**The more skills your workspace has, the faster your work gets.** Each captured skill is your team's knowledge saved permanently — it doesn't get forgotten, doesn't need retraining, and works the same way every time.

### 8. Use What You Already Have

Your workspace already has skills built for common tasks. Before asking from scratch:

- **Check existing skills:** Type `/` to see available commands
- **Use the right skill for the job:** Each skill is optimized for a specific task and will give better results than a general request

## Anti-Patterns

- **Don't dump all tips at once.** Pick the 3-5 most relevant to what the user is doing.
- **Don't be preachy.** These are practical shortcuts, not lectures.
- **Don't use technical jargon.** No "prompting", "tokens", "context window" — speak in plain language.
- **Don't make the user feel bad for asking.** Every question is valid. Frame tips as "here's a shortcut" not "you're doing it wrong."
