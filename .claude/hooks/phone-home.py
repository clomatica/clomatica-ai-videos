#!/usr/bin/env python3
"""Olympus workspace heartbeat — runs on Claude Code SessionStart.

Posts a once-per-day activity ping to the Olympus reports API so the consulting
team can see the workspace is alive, without the client ever running
/contact-olympus. Fails silently — never blocks or interrupts a session. Exits 0 always.
"""

import datetime
import json
import os
import subprocess
import sys
import urllib.request


def main():
    # Hooks run with CWD = project root; self-locate from __file__ as a fallback.
    here = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.abspath(os.path.join(here, "..", ".."))

    config_path = os.path.join(
        project_dir, ".claude", "skills", "workspace", "contact-olympus",
        "references", "olympus-workspace.json"
    )
    try:
        # utf-8-sig: tolerate a BOM (the Windows installer writes one).
        with open(config_path, encoding="utf-8-sig") as f:
            config = json.load(f)
        session_code = config.get("session_code", "")
        endpoint = config.get("report_endpoint", "")
    except Exception:
        return  # no config — nothing to do

    if not session_code or not endpoint or "{{" in session_code:
        return

    today = datetime.date.today().isoformat()

    stamp_path = os.path.join(project_dir, ".claude", "logs", ".last-activity-ping")
    first_run = True
    try:
        with open(stamp_path) as f:
            stamp = f.read().strip()
        first_run = False
        if stamp == today:
            return  # already pinged today
    except Exception:
        pass

    # Lightweight snapshot — no proprietary data, no file contents.
    skills_total = 0
    try:
        skills_dir = os.path.join(project_dir, ".claude", "skills")
        for _root, _dirs, files in os.walk(skills_dir):
            if "SKILL.md" in files:
                skills_total += 1
    except Exception:
        pass

    last_commit = None
    try:
        result = subprocess.run(
            ["git", "-C", project_dir, "log", "-1", "--format=%cI"],
            capture_output=True, text=True, timeout=3,
        )
        last_commit = result.stdout.strip() or None
    except Exception:
        pass

    payload = json.dumps({
        "session_id": session_code,
        "report_type": "activity",
        "content": {
            "ping_date": today,
            "first_run": first_run,
            "skills_total": skills_total,
            "last_commit": last_commit,
            "source": "session-start-hook",
        },
    }).encode("utf-8")

    try:
        req = urllib.request.Request(
            endpoint, data=payload,
            headers={"Content-Type": "application/json"}, method="POST",
        )
        urllib.request.urlopen(req, timeout=4).read()
    except Exception:
        return  # offline / API down — try again next session

    # Record success so we ping at most once per day.
    try:
        os.makedirs(os.path.dirname(stamp_path), exist_ok=True)
        with open(stamp_path, "w") as f:
            f.write(today)
    except Exception:
        pass


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass
    sys.exit(0)

