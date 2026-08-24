#!/usr/bin/env python3
"""Read-only git/worklist workflow signals for $workflow-analysis. No LLM calls."""
import json
import re
import subprocess
import sys
from datetime import datetime, timezone


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else ""


def git_signals(repo_path, weeks_back=12):
    def git(*args):
        return run(["git", "-C", repo_path] + list(args))

    since = f"{weeks_back * 7}.days.ago"
    log = git("log", f"--since={since}", "--pretty=%H %ct").strip().splitlines()
    weeks = {}
    for line in log:
        if not line.strip():
            continue
        _, ts = line.split()
        wk = datetime.fromtimestamp(int(ts), tz=timezone.utc).strftime("%G-W%V")
        weeks[wk] = weeks.get(wk, 0) + 1

    reverts = len([
        l for l in git("log", f"--since={since}", "--grep=^Revert", "--oneline").strip().splitlines() if l
    ])

    branches = [
        b for b in git(
            "for-each-ref", "--format=%(refname:short) %(committerdate:unix)", "refs/heads/"
        ).strip().splitlines() if b
    ]
    now = datetime.now(timezone.utc).timestamp()
    stale = 0
    for b in branches:
        parts = b.rsplit(" ", 1)
        if len(parts) == 2 and parts[1].isdigit():
            if now - int(parts[1]) > 60 * 86400:
                stale += 1

    pr_json = run([
        "gh", "pr", "list", "--repo", repo_path, "--state", "merged", "--limit", "30",
        "--json", "createdAt,mergedAt",
    ])
    turnarounds = []
    try:
        for pr in json.loads(pr_json or "[]"):
            created = datetime.fromisoformat(pr["createdAt"].replace("Z", "+00:00"))
            merged = datetime.fromisoformat(pr["mergedAt"].replace("Z", "+00:00"))
            turnarounds.append(round((merged - created).total_seconds() / 3600, 1))
    except Exception:
        pass

    return {
        "repo": repo_path,
        "window_weeks": weeks_back,
        "commits_per_week": weeks,
        "reverts": reverts,
        "stale_branches_60d": stale,
        "pr_turnaround_hours_merged_last_30": sorted(turnarounds),
    }


def worklist_signals(path):
    try:
        text = open(path).read()
    except FileNotFoundError:
        return {"error": f"no worklist at {path}"}

    items = re.findall(r"^\s*-\s+(?!\[\[).+$", text, re.MULTILINE)
    open_items = [
        i for i in items
        if not (("[[gh:" in i) and ("merged" in i or ("closed" in i and "not merged" not in i)))
    ]
    blocked = [i for i in items if "still open" in i]

    return {
        "worklist_path": path,
        "total_items": len(items),
        "open_items": len(open_items),
        "blocked_items": len(blocked),
        "blocked_examples": blocked[:5],
    }


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "git"
    if mode == "git":
        target = sys.argv[2] if len(sys.argv) > 2 else "."
        print(json.dumps(git_signals(target), indent=2))
    elif mode == "worklist":
        if len(sys.argv) < 3:
            print(json.dumps({"error": "usage: workflow_signals.py worklist <path>"}))
            sys.exit(1)
        print(json.dumps(worklist_signals(sys.argv[2]), indent=2))
    else:
        print(json.dumps({"error": f"unknown mode {mode!r}, expected git|worklist"}))
        sys.exit(1)
